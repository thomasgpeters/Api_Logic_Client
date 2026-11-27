-- Northwind, the classic schema (table and column names as in the widely used SQLite port), with its foreign keys
-- and a few rows - a test fixture for tools/pages_reference.py (the page designer's links). Not the full data.
CREATE TABLE "Categories" ( "CategoryID" INTEGER PRIMARY KEY AUTOINCREMENT, "CategoryName" TEXT, "Description" TEXT, "Picture" BLOB );
CREATE TABLE "CustomerDemographics" ( "CustomerTypeID" TEXT NOT NULL, "CustomerDesc" TEXT, PRIMARY KEY ("CustomerTypeID") );
CREATE TABLE "Customers" ( "CustomerID" TEXT, "CompanyName" TEXT, "ContactName" TEXT, "ContactTitle" TEXT, "Address" TEXT,
  "City" TEXT, "Region" TEXT, "PostalCode" TEXT, "Country" TEXT, "Phone" TEXT, "Fax" TEXT, PRIMARY KEY ("CustomerID") );
CREATE TABLE "CustomerCustomerDemo" ( "CustomerID" TEXT NOT NULL, "CustomerTypeID" TEXT NOT NULL,
  PRIMARY KEY ("CustomerID","CustomerTypeID"),
  FOREIGN KEY ("CustomerID") REFERENCES "Customers" ("CustomerID"),
  FOREIGN KEY ("CustomerTypeID") REFERENCES "CustomerDemographics" ("CustomerTypeID") );
CREATE TABLE "Employees" ( "EmployeeID" INTEGER PRIMARY KEY AUTOINCREMENT, "LastName" TEXT, "FirstName" TEXT, "Title" TEXT,
  "TitleOfCourtesy" TEXT, "BirthDate" DATE, "HireDate" DATE, "Address" TEXT, "City" TEXT, "Region" TEXT, "PostalCode" TEXT,
  "Country" TEXT, "HomePhone" TEXT, "Extension" TEXT, "Photo" BLOB, "Notes" TEXT, "ReportsTo" INTEGER, "PhotoPath" TEXT,
  FOREIGN KEY ("ReportsTo") REFERENCES "Employees" ("EmployeeID") );
CREATE TABLE "Region" ( "RegionID" INTEGER NOT NULL PRIMARY KEY, "RegionDescription" TEXT NOT NULL );
CREATE TABLE "Territories" ( "TerritoryID" TEXT NOT NULL, "TerritoryDescription" TEXT NOT NULL, "RegionID" INTEGER NOT NULL,
  PRIMARY KEY ("TerritoryID"), FOREIGN KEY ("RegionID") REFERENCES "Region" ("RegionID") );
CREATE TABLE "EmployeeTerritories" ( "EmployeeID" INTEGER NOT NULL, "TerritoryID" TEXT NOT NULL,
  PRIMARY KEY ("EmployeeID","TerritoryID"),
  FOREIGN KEY ("EmployeeID") REFERENCES "Employees" ("EmployeeID"),
  FOREIGN KEY ("TerritoryID") REFERENCES "Territories" ("TerritoryID") );
CREATE TABLE "Shippers" ( "ShipperID" INTEGER PRIMARY KEY AUTOINCREMENT, "CompanyName" TEXT NOT NULL, "Phone" TEXT );
CREATE TABLE "Suppliers" ( "SupplierID" INTEGER PRIMARY KEY AUTOINCREMENT, "CompanyName" TEXT NOT NULL, "ContactName" TEXT,
  "ContactTitle" TEXT, "Address" TEXT, "City" TEXT, "Region" TEXT, "PostalCode" TEXT, "Country" TEXT, "Phone" TEXT,
  "Fax" TEXT, "HomePage" TEXT );
CREATE TABLE "Products" ( "ProductID" INTEGER PRIMARY KEY AUTOINCREMENT, "ProductName" TEXT NOT NULL, "SupplierID" INTEGER,
  "CategoryID" INTEGER, "QuantityPerUnit" TEXT, "UnitPrice" NUMERIC DEFAULT 0, "UnitsInStock" INTEGER DEFAULT 0,
  "UnitsOnOrder" INTEGER DEFAULT 0, "ReorderLevel" INTEGER DEFAULT 0, "Discontinued" TEXT NOT NULL DEFAULT '0',
  FOREIGN KEY ("CategoryID") REFERENCES "Categories" ("CategoryID"),
  FOREIGN KEY ("SupplierID") REFERENCES "Suppliers" ("SupplierID") );
CREATE TABLE "Orders" ( "OrderID" INTEGER PRIMARY KEY AUTOINCREMENT, "CustomerID" TEXT, "EmployeeID" INTEGER, "OrderDate" DATETIME,
  "RequiredDate" DATETIME, "ShippedDate" DATETIME, "ShipVia" INTEGER, "Freight" NUMERIC DEFAULT 0, "ShipName" TEXT,
  "ShipAddress" TEXT, "ShipCity" TEXT, "ShipRegion" TEXT, "ShipPostalCode" TEXT, "ShipCountry" TEXT,
  FOREIGN KEY ("EmployeeID") REFERENCES "Employees" ("EmployeeID"),
  FOREIGN KEY ("CustomerID") REFERENCES "Customers" ("CustomerID"),
  FOREIGN KEY ("ShipVia") REFERENCES "Shippers" ("ShipperID") );
CREATE TABLE "Order Details" ( "OrderID" INTEGER NOT NULL, "ProductID" INTEGER NOT NULL, "UnitPrice" NUMERIC NOT NULL DEFAULT 0,
  "Quantity" INTEGER NOT NULL DEFAULT 1, "Discount" REAL NOT NULL DEFAULT 0, PRIMARY KEY ("OrderID","ProductID"),
  FOREIGN KEY ("OrderID") REFERENCES "Orders" ("OrderID"),
  FOREIGN KEY ("ProductID") REFERENCES "Products" ("ProductID") );

INSERT INTO "Categories" VALUES (1,'Beverages','Soft drinks, coffees, teas, beers, and ales',NULL),
  (2,'Condiments','Sweet and savory sauces, relishes, spreads, and seasonings',NULL),
  (4,'Dairy Products','Cheeses',NULL), (5,'Grains/Cereals','Breads, crackers, pasta, and cereal',NULL);
INSERT INTO "Suppliers" ("SupplierID","CompanyName","City","Country") VALUES (1,'Exotic Liquids','London','UK'),
  (5,'Cooperativa de Quesos ''Las Cabras''','Oviedo','Spain'), (9,'PB Knäckebröd AB','Göteborg','Sweden'),
  (15,'Norske Meierier','Sandvika','Norway');
INSERT INTO "Products" ("ProductID","ProductName","SupplierID","CategoryID","UnitPrice") VALUES
  (1,'Chai',1,1,18), (11,'Queso Cabrales',5,4,21), (22,'Gustaf''s Knäckebröd',9,5,21), (42,'Singaporean Hokkien Fried Mee',9,5,14),
  (72,'Mozzarella di Giovanni',15,4,34.8);
INSERT INTO "Customers" ("CustomerID","CompanyName","City","Country") VALUES ('VINET','Vins et alcools Chevalier','Reims','France'),
  ('TOMSP','Toms Spezialitäten','Münster','Germany'), ('ALFKI','Alfreds Futterkiste','Berlin','Germany');
INSERT INTO "Employees" ("EmployeeID","LastName","FirstName","Title","ReportsTo") VALUES (2,'Fuller','Andrew','Vice President, Sales',NULL),
  (5,'Buchanan','Steven','Sales Manager',2), (6,'Suyama','Michael','Sales Representative',5);
INSERT INTO "Shippers" VALUES (1,'Speedy Express','(503) 555-9831'), (3,'Federal Shipping','(503) 555-9931');
INSERT INTO "Orders" ("OrderID","CustomerID","EmployeeID","OrderDate","ShipVia","Freight") VALUES
  (10248,'VINET',5,'1996-07-04',3,32.38), (10249,'TOMSP',6,'1996-07-05',1,11.61);
INSERT INTO "Order Details" VALUES (10248,11,14,12,0), (10248,42,9.8,10,0), (10248,72,34.8,5,0),
  (10249,14,18.6,9,0), (10249,51,42.4,40,0);
INSERT INTO "Region" VALUES (1,'Eastern'), (2,'Western');
INSERT INTO "Territories" VALUES ('01581','Westboro',1), ('94025','Menlo Park',2);
INSERT INTO "EmployeeTerritories" VALUES (5,'01581'), (6,'94025');
