-- Flight Planner sample: remove the sample data, keep the lookup data (children first).
-- Plain SQL: the lookup tables hold no totals of the sample data, so nothing is left to recompute.

DELETE FROM "PositionReport";
DELETE FROM "Leg";
DELETE FROM "Endorsement";
DELETE FROM "LoadItem";
DELETE FROM "FlightPlan";
DELETE FROM "Weather";
DELETE FROM "AircraftStation";
DELETE FROM "Aircraft";
DELETE FROM "LogbookEntry";
DELETE FROM "Pilot";
