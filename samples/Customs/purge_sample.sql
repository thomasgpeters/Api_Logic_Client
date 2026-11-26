-- Customs sample: remove the sample data, keep the lookup data (children first).
-- Plain SQL: the lookup tables hold no totals of the sample data, so nothing is left to recompute.

DELETE FROM "Movement";
DELETE FROM "Driver";
DELETE FROM "Truck";
DELETE FROM "Inspection";
DELETE FROM "Payment";
DELETE FROM "DeclarationLine";
DELETE FROM "Declaration";
DELETE FROM "Container";
DELETE FROM "Arrival";
DELETE FROM "Importer";
