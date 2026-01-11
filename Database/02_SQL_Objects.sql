USE KitapKurduDB;
GO

-- =============================================
-- SECTION 1: STORED PROCEDURES (SP)
-- =============================================

-- 2.1. SP_CreateOrder
-- Retrieves cart, creates order (Address removed), moves items, clears cart.
CREATE OR ALTER PROCEDURE SP_CreateOrder
    @UserID INT, 
    @TotalAmount DECIMAL(10, 2),
    @CreatedOrderID INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @CurrentCartID INT;
    
    -- 1. Retrieve User's Active Cart
    SELECT @CurrentCartID = CartID FROM Carts WHERE UserID = @UserID;
    
    IF @CurrentCartID IS NULL RETURN -1; -- Error: No Cart Found
    
    -- 2. Create New Record in Orders Table (Address Removed)
    INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, Statuss)
    VALUES (@UserID, GETDATE(), @TotalAmount, 'Pending');
    
    SET @CreatedOrderID = SCOPE_IDENTITY();

    -- 3. Transfer Items from CartItems to OrderItems
    INSERT INTO OrderItems (OrderID, BookID, Quantity, ProductPrice)
    SELECT @CreatedOrderID, CI.BookID, CI.Quantity, B.Price
    FROM CartItems CI 
    INNER JOIN Books B ON CI.BookID = B.BookID 
    WHERE CI.CartID = @CurrentCartID;

    -- 4. Clear the Shopping Cart
    DELETE FROM CartItems WHERE CartID = @CurrentCartID;
    
    RETURN 0; -- Success
END
GO

-- 2.2. SP_CalculateCartTotal
-- Calculates total monetary value of the cart.
CREATE OR ALTER PROCEDURE SP_CalculateCartTotal
    @UserID INT,
    @TotalAmount DECIMAL(10, 2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @CalculatedTotal DECIMAL(10, 2);
    
    SELECT @CalculatedTotal = SUM(CI.Quantity * B.Price)
    FROM Carts C 
    INNER JOIN CartItems CI ON C.CartID = CI.CartID 
    INNER JOIN Books B ON CI.BookID = B.BookID
    WHERE C.UserID = @UserID;
    
    SET @TotalAmount = ISNULL(@CalculatedTotal, 0);
END
GO

-- 2.3. SP_AddReview
-- Adds review only if Order is Delivered.
CREATE OR ALTER PROCEDURE SP_AddReview
    @OrderID INT,
    @UserID INT,
    @BookID INT,
    @Rating INT, 
    @Comment NVARCHAR(500)
AS
BEGIN
    DECLARE @EligibleOrderCount INT;

    -- Check business criteria: Purchased AND Delivered
    -- Note: 'Teslim Edildi' is used as 'Delivered' based on your data logic
    SELECT @EligibleOrderCount = COUNT(*)
    FROM Orders 
    WHERE OrderID = @OrderID 
      AND CustomerID = @UserID 
      AND Statuss = 'Delivered'; 

    IF @EligibleOrderCount > 0
    BEGIN
        INSERT INTO Reviews (BookID, UserID, Star, Comment) 
        VALUES (@BookID, @UserID, @Rating, @Comment);
        RETURN 1; -- Success
    END
    ELSE
    BEGIN
        RETURN 0; -- Failed (Fake review prevention)
    END
END
GO

-- 2.4. SP_UpdateOrderStatus
-- Vendor tool to update order status (e.g. Pending to Sent).
CREATE OR ALTER PROCEDURE SP_UpdateOrderStatus
    @OrderID INT,
    @NewStatus NVARCHAR(50)
AS
BEGIN
    UPDATE Orders
    SET Statuss = @NewStatus
    WHERE OrderID = @OrderID;
END
GO

-- 2.5. SP_RemoveBook
-- Grants Admin authority to remove books.
CREATE OR ALTER PROCEDURE SP_RemoveBook
    @BookID INT
AS
BEGIN
    DELETE FROM Books WHERE BookID = @BookID;
END
GO

-- 2.6. SP_UpdateStock
-- Allows vendor to manually update stock.
CREATE OR ALTER PROCEDURE SP_UpdateStock
    @BookID INT,
    @NewStock INT
AS
BEGIN
    UPDATE Books
    SET Stock = @NewStock
    WHERE BookID = @BookID;
END
GO


USE KitapKurduDB;
GO
-- =============================================
-- SECTION 2: TRIGGERS (TRG)
-- =============================================

-- 3.1. TRG_StockDecrease
-- Automatically reduces stock when an order is placed. 
-- Rollbacks transaction if stock falls below zero.
CREATE OR ALTER TRIGGER TRG_StockDecrease
ON OrderItems
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Update Stock based on Quantity Ordered
    UPDATE B
    SET B.Stock = B.Stock - I.Quantity
    FROM Books B
    INNER JOIN inserted I ON B.BookID = I.BookID;

    -- Safety Check: If stock is negative, Cancel Transaction
    IF EXISTS (SELECT 1 FROM Books WHERE Stock < 0)
    BEGIN
        ROLLBACK TRANSACTION;
        RAISERROR('Transaction Failed: Insufficient Stock.', 16, 1);
        RETURN;
    END
END
GO

-- 3.2. TRG_OrderHistoryLog
-- Logs changes in Order Status to OrderStatusHistory table.
CREATE OR ALTER TRIGGER TRG_OrderHistoryLog
ON Orders
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Execute only if 'Statuss' column is updated
    IF UPDATE(Statuss)
    BEGIN
        INSERT INTO OrderStatusHistory (OrderID, OldStatus, NewStatus, ChangeDate)
        SELECT 
            d.OrderID, 
            d.Statuss,  -- Old Status
            i.Statuss,  -- New Status
            GETDATE()
        FROM deleted d
        INNER JOIN inserted i ON d.OrderID = i.OrderID;
    END
END
GO

-- 3.3. TRG_UpdateAverageRating
-- Recalculates Book's AverageRating whenever a review is added or deleted.
CREATE OR ALTER TRIGGER TRG_UpdateAverageRating
ON Reviews
AFTER INSERT, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @AffectedBookID INT;

    -- Determine the BookID involved
    IF EXISTS (SELECT * FROM inserted)
        SELECT @AffectedBookID = BookID FROM inserted;
    ELSE
        SELECT @AffectedBookID = BookID FROM deleted;

    -- Calculate Average and Update Books Table
    UPDATE Books
    SET AverageRating = (
        SELECT ISNULL(AVG(CAST(Star AS DECIMAL(3, 2))), 0)
        FROM Reviews
        WHERE BookID = @AffectedBookID
    )
    WHERE BookID = @AffectedBookID;
END
GO

-- 3.4. TRG_LowStockNotification
-- Monitors stock levels. Inserts alert to AdminNotifications if stock <= 3.
CREATE OR ALTER TRIGGER TRG_LowStockNotification
ON Books
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if Stock column was updated
    IF UPDATE(Stock)
    BEGIN
        DECLARE @CriticalLimit INT = 3;

        INSERT INTO AdminNotifications (Message)
        SELECT 
            'URGENT: Low stock level for book: "' + i.BookName + '" (Remaining: ' + CAST(i.Stock AS NVARCHAR(10)) + ')'
        FROM inserted i
        INNER JOIN deleted d ON i.BookID = d.BookID
        -- Logic: Trigger only if stock drops to/below limit FROM a higher value
        WHERE i.Stock <= @CriticalLimit 
          AND d.Stock > @CriticalLimit; 
    END
END
GO

-- =============================================
-- SECTION 3: FUNCTIONS (FN)
-- =============================================

-- 1.1. FN_EstimatedDelivery
-- Calculates estimated delivery date based on business logic.
-- Logic: Weekends (Fri, Sat, Sun) -> +5 Days, Weekdays -> +3 Days.
CREATE OR ALTER FUNCTION FN_EstimatedDelivery (@OrderDate DATETIME)
RETURNS DATETIME
AS
BEGIN
    DECLARE @DeliveryDate DATETIME;
    DECLARE @DayOfWeek INT;
    
    -- Default to current date if NULL
    IF @OrderDate IS NULL SET @OrderDate = GETDATE();

    -- Get day of week (SQL Server default usually starts Sunday=1 or Monday=1 depending on settings)
    -- Using DATEPART(WEEKDAY) is the standard approach.
    SET @DayOfWeek = DATEPART(WEEKDAY, @OrderDate);

    -- Logic: Assuming standard US settings (Sun=1, Sat=7) or TR settings.
    -- To be safe and generic: If day is Fri(6), Sat(7), Sun(1) -> Add 5 Days.
    -- (Adjust logic if server settings differ, but this covers the weekend concept)
    
    IF @DayOfWeek IN (1, 6, 7) -- Sunday, Friday, Saturday (approx)
        SET @DeliveryDate = DATEADD(DAY, 5, @OrderDate);
    ELSE
        SET @DeliveryDate = DATEADD(DAY, 3, @OrderDate);

    RETURN @DeliveryDate;
END
GO

-- 1.2. FN_HideName_Details
-- Masks full names for privacy compliance (GDPR/KVKK) in Admin Panel and Reviews.
-- Example: "Ali Yilmaz" -> "A** Y*****"
CREATE OR ALTER FUNCTION FN_HideName_Details (@FullName NVARCHAR(100))
RETURNS NVARCHAR(100)
AS
BEGIN
    -- Null or too short check
    IF @FullName IS NULL OR LEN(@FullName) < 2 RETURN '';

    DECLARE @SpaceIndex INT;
    DECLARE @FirstName NVARCHAR(50);
    DECLARE @LastName NVARCHAR(50);
    DECLARE @MaskedResult NVARCHAR(100);

    -- Find the space between First Name and Last Name
    SET @SpaceIndex = CHARINDEX(' ', @FullName);

    IF @SpaceIndex = 0
    BEGIN
        -- Case: Single name (No space) -> Mask all except first letter
        SET @MaskedResult = LEFT(@FullName, 1) + REPLICATE('*', LEN(@FullName) - 1);
    END
    ELSE
    BEGIN
        -- Case: First Name + Last Name
        
        -- Process First Name
        SET @FirstName = SUBSTRING(@FullName, 1, @SpaceIndex - 1);
        DECLARE @MaskedFirst NVARCHAR(50) = LEFT(@FirstName, 1) + REPLICATE('*', LEN(@FirstName) - 1);

        -- Process Last Name
        SET @LastName = SUBSTRING(@FullName, @SpaceIndex + 1, LEN(@FullName) - @SpaceIndex);
        DECLARE @MaskedLast NVARCHAR(50) = LEFT(@LastName, 1) + REPLICATE('*', LEN(@LastName) - 1);

        -- Combine
        SET @MaskedResult = @MaskedFirst + ' ' + @MaskedLast;
    END

    RETURN @MaskedResult;
END
GO
-- 1.3.FN_GetTotalBookSales
--This code goes to the OrderItems table and calculates the total number of units sold for the book ID you provide.
CREATE FUNCTION dbo.FN_GetTotalBookSales (@BookID INT)
RETURNS INT
AS
BEGIN
    DECLARE @TotalSold INT;

   -- Add up all the Quantity values ​​in the OrderItems table of that book.
    SELECT @TotalSold = SUM(Quantity) 
    FROM OrderItems 
    WHERE BookID = @BookID;

   -- If it hasn't been sold at all (returns NULL), the result will be 0.
    IF @TotalSold IS NULL
        SET @TotalSold = 0;

    RETURN @TotalSold;
END

-- =============================================
-- SECTION 4: VIEWS (VW)
-- =============================================

-- 4.1. VW_OrderDetails
-- Comprehensive reporting tool. Joins Orders, Users, OrderItems, Books.
CREATE OR ALTER VIEW VW_OrderDetails
AS
SELECT 
    O.OrderID,
    O.CustomerID, 
    ISNULL(U.FullName, 'Guest') AS CustomerName,
    O.OrderDate,
    ISNULL(B.BookName, 'Unknown') AS BookTitle,
    B.BookID,
    ISNULL(OI.Quantity, 0) AS Quantity,
    ISNULL(OI.ProductPrice, 0) AS UnitPrice,
    ISNULL((OI.Quantity * OI.ProductPrice), 0) AS LineTotal,
    O.Statuss AS OrderStatus

FROM Orders O
LEFT JOIN Users U ON O.CustomerID = U.UserID      
LEFT JOIN OrderItems OI ON O.OrderID = OI.OrderID 
LEFT JOIN Books B ON OI.BookID = B.BookID;       
GO