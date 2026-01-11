USE master;
GO

-- If database exists, drop it to start fresh
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'KitapKurduDB')
BEGIN
    DROP DATABASE KitapKurduDB;
END
GO

CREATE DATABASE KitapKurduDB;
GO

USE KitapKurduDB;
GO

-- =============================================
-- 1. TABLES CREATION
-- =============================================

-- Users Table
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    Email VARCHAR(150) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(200) NOT NULL,
    UserType VARCHAR(20) NOT NULL DEFAULT 'customer' -- 'admin' or 'customer'
);

-- Categories Table
CREATE TABLE Categories (
    CategoryID INT IDENTITY(1,1) PRIMARY KEY, 
    CategoryName NVARCHAR(100) NOT NULL
);

-- Books Table
CREATE TABLE Books (
    BookID INT IDENTITY(1,1) PRIMARY KEY,
    BookName NVARCHAR(100) NOT NULL,
    CategoryID INT NOT NULL,
    Author NVARCHAR(100) NOT NULL,
    Price DECIMAL(6,2) NOT NULL,
    Stock INT NOT NULL DEFAULT 0,
    ImageUrl NVARCHAR(300) NULL,           
    AverageRating DECIMAL(3,2) DEFAULT 0   
);

-- Orders Table
CREATE TABLE Orders (
    OrderID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL,
    Statuss VARCHAR(30) NOT NULL DEFAULT 'Order Received', 
    OrderDate DATETIME NOT NULL DEFAULT GETDATE(),
    TotalAmount DECIMAL(10,2) NOT NULL
);

-- Order Items Table
CREATE TABLE OrderItems (
    OrderItemID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NOT NULL,
    BookID INT NOT NULL,
    Quantity INT NOT NULL,
    ProductPrice DECIMAL(6,2) NOT NULL
);

-- Reviews Table
CREATE TABLE Reviews (
    RewiewID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    BookID INT NOT NULL,
    Star INT NOT NULL,
    Comment NVARCHAR(500) NULL
);

-- Shopping Carts Table
CREATE TABLE Carts (
    CartID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,                  
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE()
);

-- Cart Items Table
CREATE TABLE CartItems (
    CartItemID INT IDENTITY(1,1) PRIMARY KEY,
    CartID INT NOT NULL,                  
    BookID INT NOT NULL,                  
    Quantity INT NOT NULL,                
    CONSTRAINT UQ_CartItem UNIQUE (CartID, BookID) 
);

-- Favorites Table
CREATE TABLE Favorites (
    FavoriteID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    BookID INT NOT NULL
);

-- Order Status History (Audit Log)
CREATE TABLE OrderStatusHistory (
    HistoryID INT PRIMARY KEY IDENTITY(1,1),
    OrderID INT,
    OldStatus NVARCHAR(50),
    NewStatus NVARCHAR(50),
    ChangeDate DATETIME DEFAULT GETDATE()
);

-- Admin Notifications (System Alerts)
CREATE TABLE AdminNotifications (
    NotificationID INT PRIMARY KEY IDENTITY(1,1),
    Message NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- =============================================
-- 2. FOREIGN KEYS (RELATIONSHIPS)
-- =============================================

ALTER TABLE Books ADD CONSTRAINT FK_Books_Categories FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID);
ALTER TABLE Orders ADD CONSTRAINT FK_Orders_Users FOREIGN KEY (CustomerID) REFERENCES Users(UserID);
ALTER TABLE OrderItems ADD CONSTRAINT FK_OrderItems_Orders FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);
ALTER TABLE OrderItems ADD CONSTRAINT FK_OrderItems_Books FOREIGN KEY (BookID) REFERENCES Books(BookID);
ALTER TABLE Reviews ADD CONSTRAINT FK_Reviews_Users FOREIGN KEY (UserID) REFERENCES Users(UserID);
ALTER TABLE Reviews ADD CONSTRAINT FK_Reviews_Books FOREIGN KEY (BookID) REFERENCES Books(BookID);
ALTER TABLE Favorites ADD CONSTRAINT FK_Favorites_Users FOREIGN KEY (UserID) REFERENCES Users(UserID);
ALTER TABLE Favorites ADD CONSTRAINT FK_Favorites_Books FOREIGN KEY (BookID) REFERENCES Books(BookID);
ALTER TABLE Carts ADD CONSTRAINT FK_Carts_Users FOREIGN KEY (UserID) REFERENCES Users(UserID);
ALTER TABLE CartItems ADD CONSTRAINT FK_CartItems_Carts FOREIGN KEY (CartID) REFERENCES Carts(CartID);
ALTER TABLE CartItems ADD CONSTRAINT FK_CartItems_Books FOREIGN KEY (BookID) REFERENCES Books(BookID);

PRINT '>>> Database setup completed successfully.';