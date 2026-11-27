-- Customs sample: remove the sample data, keep the lookup data (children first).
-- Plain SQL: the lookup tables hold no totals of the sample data, so nothing is left to recompute.

DELETE FROM "Movement";
DELETE FROM "Driver";
DELETE FROM "Truck";
DELETE FROM "Payment";
DELETE FROM "Inspection";
DELETE FROM "Hold";
DELETE FROM "Permit";
DELETE FROM "DeclarationLine";
DELETE FROM "Declaration";
DELETE FROM "Container";
DELETE FROM "HouseBill";
DELETE FROM "MasterBill";
DELETE FROM "Arrival";
DELETE FROM "Statement";
DELETE FROM "Importer";
