-- Flight Planner sample: remove the sample data, keep the lookup data (children first).
-- Plain SQL: the lookup tables hold no totals of the sample data, so nothing is left to recompute.

DELETE FROM "PositionReport";
DELETE FROM "Leg";
DELETE FROM "FlightPlan";
DELETE FROM "Aircraft";
DELETE FROM "Pilot";
