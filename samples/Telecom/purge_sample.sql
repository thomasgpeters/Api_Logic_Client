-- Telecom sample: remove the sample data, keep the lookup data (children first).
-- Plain SQL: the lookup tables hold no totals of the sample data, so nothing is left to recompute.

DELETE FROM "TravelPlanCountry";
DELETE FROM "TravelPlan";
DELETE FROM "Usage";
DELETE FROM "Phone";
DELETE FROM "Plan";
DELETE FROM "Account";
DELETE FROM "Customer";
