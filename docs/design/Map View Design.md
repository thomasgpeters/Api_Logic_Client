# Map view: a result set on a map (design)

The author (2026-11-25): a look with a map. Generic: choose the Map view and it shows a **result
set** whose rows carry a geographic location - **latitude and longitude columns**. Start with an
entity's records (Customer, Supplier, …); any query's result set later. Addresses are translated
into locations to fill those columns where a table has none. A design to agree before building;
the steps are in `BACKLOG.md` → Modern look → Map view.

## The idea in one line

    a result set (rows)  +  which columns are latitude, longitude, title  ->  pins on a map

The map knows nothing about Customers: it takes rows and the names of their columns. So the same
map shows Customers, Suppliers, both at once (one colour each), or the rows of any query the SQL
Generator (or its JSON:API side) returns - as long as each row has a latitude and a longitude.

## What the user sees

- **List | Map** above an entity's records: Map shows the rows the List shows (the same filter),
  one pin per row with its latitude and longitude, titled by the display column (Customer:
  `CompanyName`) with a second line (city, country). Rows without a location are counted in the
  footer: *"84 of 91 customers on the map - 7 have no location"*.
- Clicking a pin selects the row and opens its Form, as a click in the List does.
- **More than one result set on a map** (step 2): e.g. Customers and Suppliers together, each a
  layer with its own pin colour and a checkbox to show or hide it.
- **Any result set** (step 3): a query's rows - e.g. "Customers with orders over 10,000" - shown
  on the map the same way.

## The location columns

The map needs a latitude and a longitude in each row. The Studio finds them in the model by name
and type (the designer can change the choice, `Design.json`):

| Found | Names |
|---|---|
| latitude | `Latitude`, `Lat`, `<prefix>Latitude` (REAL / DECIMAL / NUMERIC) |
| longitude | `Longitude`, `Long`, `Lng`, `Lon`, `<prefix>Longitude` |

An entity with both gets the Map view. **Northwind has none** - its Customers, Employees and
Suppliers have addresses (Address, City, Region, PostalCode, Country) and its Orders ship-to
addresses (Ship…). For those the Studio offers to **add the location columns and fill them**:

- **Lite:** `ALTER TABLE <table> ADD COLUMN Latitude REAL` and `… Longitude REAL` in the project's
  database copy (harmless when they exist), the model read again; then the app fills them (below).
- **Enterprise:** the columns belong to the server's database and model: the Studio says which
  columns to add, and that the ALS project is then rebuilt (`ApiLogicServer rebuild-from-database`);
  the Studio reads the new `models.py`. The app fills them through the server (PATCH).

## Filling the columns: address -> location (geocoding)

From the address columns of the same row (Address, City, Region, PostalCode, Country, or a prefixed
family), joined into one line. FutureBasic has it all (`Tlbx MapKit.incl`; FBExamples *MKMapView /
Coordinates from address*):

- `CLGeocoderGeocodeAddressString( fn CLGeocoderInit, address, @fn Handler, userData )` - Apple's
  geocoder: no API key, no cost, no location permission. The answer comes to a handler:
  `CLPlacemarkLocation`, `CLLocationCoordinate`. On macOS 26 `MKGeocodingRequestWithAddressString`
  (CLGeocoder is deprecated there but works); the runtime picks by OS version, as `Pill Buttons.incl` does.
- Apple limits how fast an app may geocode: **one address at a time** from a queue, spaced out; a
  throttling or network error puts the row back for later. Progress in the footer.
- The answer is **written into the row's Latitude / Longitude** - Lite through the rules engine
  (`LogicUpdate`), Enterprise through the server - so the location is stored with the record, the
  map reads columns only, and every other result set (a query, a report) has it too.
- When: a *Locate* action on the page (the rows without a location), and after a Save that changed
  an address column (the location is cleared and looked up again).
- An address that cannot be found keeps an empty location and is listed, never guessed.
- The addresses go to Apple's service: the generated app's README says so.

## Where it lives

| | |
|---|---|
| `src/Runtime/App Map.incl` | the generic map: `mkmapview`; `MapShowRows( mapTag, layer, rows, latitudeKey, longitudeKey, titleKey, subtitleKey )` -> pins (`MKPointAnnotationWithTitle`, `MKMapViewShowAnnotations`); layers with colours; `_mapViewDidSelectAnnotationView` -> the layer and row |
| `src/Runtime/Geo Location.incl` | address -> location: the queue, CLGeocoder / MKGeocodingRequest, writing Latitude / Longitude through App Data |
| `src/Generator/Type Mapping.incl` | the location columns (found or chosen), the address family, the entity's Map setting |
| `src/Generator/` | *Add Location Columns* (Lite: ALTER TABLE in the project's copy; Enterprise: instructions); the List \| Map switch and the row -> pin keys per entity in the generated pages |

## Steps

1. One entity's result set on a map (Customer): the location columns found or chosen; the generic
   `App Map.incl`; List | Map; pin -> Form.
2. Several result sets on one map (Customers and Suppliers): layers, colours, show / hide.
3. Any result set: a query's rows (SQL Generator / JSON:API) on the map.
4. Filling the columns: *Add Location Columns* in the Studio; *Locate* in the app (geocoding).
5. Later: clustering many pins; directions between rows; a small map on the Form.

## Open questions (author)

- Northwind has no location columns: add `Latitude` / `Longitude` to Customer and Supplier in the
  project's copy (Lite) so step 1 has data - or start with a test database that has them?
- Column names: `Latitude` / `Longitude` (proposed) for the columns the Studio adds?
- Step 2's layers: one colour per entity chosen in the Studio, or the system's palette in order?
