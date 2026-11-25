# Map view: records on a map (design)

The author (2026-11-25): another look for a generated app - the records of an entity (Customers)
placed on a map, with addresses translated into geographic locations. A design to agree before
building; the steps are in `BACKLOG.md` → Modern look → Map view.

## What the user sees

An entity whose records have a place gets a **Map** beside its List: a List | Map switch above the
records. The map shows a pin for each record the List shows (the same filter), titled by the
record's display column (Customer: `CompanyName`) with the city and country below. Clicking a pin
selects the record and opens its Form, as a click in the List does. While addresses are being
looked up, the footer says so: *"Placing 12 of 91 customers on the map…"*; an address that cannot
be found is listed, not guessed.

## Which entities, which columns

The Studio finds them in the model, and the designer can change the choice (`Design.json`, like
the Form layout):

| The entity has | The map uses |
|---|---|
| latitude / longitude columns (`Latitude`, `Longitude`, `lat`, `lng`, `lon`) | them directly - no lookup |
| an address family: street (`Address`, `Street`), `City`, `Region` / `State`, `PostalCode` / `Zip`, `Country` | the address, looked up once and remembered |
| a prefixed family (`ShipAddress`, `ShipCity`, … on Order) | the same, under that prefix; an entity can have more than one (choose one) |

Northwind: Customer, Employee and Supplier (address), Order (ship-to address). The CRM: Address.

## Address -> location (geocoding)

FutureBasic has all of it (`Tlbx MapKit.incl`; FBExamples *MKMapView / Coordinates from address*):

- `CLGeocoderGeocodeAddressString( fn CLGeocoderInit, address, @fn Handler, userData )` - Apple's
  geocoder: no API key, no cost, no location permission (forward geocoding does not locate the
  user). The answer comes to a handler with placemarks; `CLPlacemarkLocation`, `CLLocationCoordinate`.
- macOS 26 adds `MKGeocodingRequestWithAddressString` / `MKGeocodingRequestGetMapItems`
  (CLGeocoder is deprecated there but still works): the runtime picks by OS version, as
  `Pill Buttons.incl` does.
- Apple limits how fast an app may geocode, so the runtime looks up **one address at a time**,
  spaced out, from a queue; a throttling or network error puts the address back for later.
- **Remembered, not repeated:** each answer is kept in a cache - `GeoCache.sqlite` in the app's
  Application Support folder: `address TEXT PRIMARY KEY, latitude, longitude, found, looked_up`.
  The key is the address as sent (trimmed, one space, lower-case). A changed address is a new key,
  so an edited record is placed again. The model's database is not touched, and the cache works
  the same for both editions.
- Optionally (a designer choice), the coordinates are written into the record's own latitude /
  longitude columns when it has them - in Lite through the rules engine; in Enterprise through the
  server (a PATCH).
- The addresses go to Apple's service: the generated app's README says so.

## Where it lives

| | |
|---|---|
| `src/Runtime/Geo Location.incl` | the queue, the geocoder (CLGeocoder / MKGeocodingRequest), the cache |
| `src/Runtime/App Map.incl` | the Map part: `mkmapview`, pins (`MKPointAnnotationWithTitle`, `MKMapViewShowAnnotations`), the selection event (`_mapViewDidSelectAnnotationView`) -> the record |
| `src/Generator/Type Mapping.incl` | which columns make a place (recommended), the entity's Map setting |
| `src/Generator/App Generator.incl`, Binding Generator | the List \| Map switch, the record -> pin mapping per entity |

## Open questions (author)

- The cache in its own file (proposed) or a table in the app's database?
- Write coordinates back into the records when the table has latitude / longitude columns - on by default?
- Many pins: clustering (MapKit's cluster annotations) from the start, or later?
- Later: directions between records (FBExamples *MKMapView - directions*), a map on the Form showing just that record.
