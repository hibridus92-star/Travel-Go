# Travel&Go: requirements

Last updated: November 2026

This document defines what Travel&Go must do. It is the reference for the design, the code and the tests, and it must be updated in the same branch as any change to the model.

Requirement IDs are grouped by area (`TRP-03`, `VCH-02`...), so adding a requirement never forces renumbering the others. The status of each requirement is **Done**, **Partly done** or **Planned**; the delivery order is in the roadmap of the [README](../README.md).

## 1. Scope

**In scope:** planning the activities of a trip once the user has chosen the destination and the length of the stay, and a loyalty system built around points, discounts, transferable vouchers and local hosts.

**Out of scope:** accommodation, transport, real payments, user authentication and cancellations or refunds (see [Known limitations](#6-known-limitations)).

## 2. Glossary

| Term | Meaning |
|---|---|
| Activity | A bookable plan at the destination, with a price per person and a date and time. Today: guided tour and pub crawl. |
| Trip | A destination, a date range, a set of activities and a set of participants. |
| Owner | The user who books a trip. Only the owner pays and earns the benefits of the purchase. |
| Participant | A registered user taking part in a trip. The owner is also a participant. |
| Travel points | The loyalty balance of a user. They can be exchanged for discounts or turned into vouchers. |
| Voucher | A code that carries a fixed number of points. Issued by one user, redeemable only by a new user. |
| New user | A user with no purchases who registered 30 days ago or less. |
| Host | A user certified as a local guide who organises activities. The code calls the profile `GuideProfile`. |
| Tip | Money given on top of the price to the host of an activity. It goes to Travel&Go. |

## 3. Functional requirements

### 3.1 Activities (ACT)

| ID | Requirement | Status |
|---|---|---|
| ACT-01 | An activity has a name, a city, a venue, a price per person and a date and time. | Partly done (name, venue, price) |
| ACT-02 | There are two kinds of activity, guided tour and pub crawl, and a new kind can be added without changing the existing ones. | Done |
| ACT-03 | An activity is saved with its type and restored as an object of the right class. | Done |
| ACT-04 | A price is a non-negative decimal with at most two decimals. A name cannot be empty or only spaces. Prices are saved as text (for example `"25.90"`), and files that saved them as numbers still load. | Done |
| ACT-05 | Activities come from a catalogue maintained by the platform. Users choose activities, they do not create them. | Planned |
| ACT-06 | An activity exists on its own and can belong to several trips. | Done |

### 3.2 Trips (TRP)

| ID | Requirement | Status |
|---|---|---|
| TRP-01 | A trip has a destination, a start date, an end date and a unique ID (a UUID stored as text). | Partly done (destination, integer ID) |
| TRP-02 | The date and time of every activity must fall inside the trip dates, limits included. It is checked when the activity is added. | Planned |
| TRP-03 | The owner is added automatically as a participant. All participants have the same rights over the trip. | Planned |
| TRP-04 | Participants are registered users stored by ID. A duplicate participant or the removal of an unknown one is rejected. | Done |
| TRP-05 | A trip is a **draft** (activities and participants can change) or **purchased** (locked, nothing can change). | Planned |
| TRP-06 | The price per person is the sum of the prices of the activities. The total price is that amount multiplied by the number of participants. | Partly done (sum of prices) |
| TRP-07 | Each trip is saved in `data/trips/<trip_id>.json` and can be loaded by its ID. Loading a missing trip is an error. Old files without the new fields still load. | Planned |
| TRP-08 | Showing a trip lists the names of its participants, not their IDs. | Planned |
| TRP-09 | A trip can describe itself, calculate its cost and count its alcoholic activities. | Done |

### 3.3 Users (USR)

| ID | Requirement | Status |
|---|---|---|
| USR-01 | A user has a name, a surname, a birth date, a city, a country, languages and a registration date. | Partly done (registration date missing) |
| USR-02 | Each user has a unique ID (a UUID). No personal data is used as an identifier. | Done |
| USR-03 | The age is calculated from the birth date. | Done |
| USR-04 | Languages are ISO 639-1 codes (`en`, `es`) and are validated. | Planned |
| USR-05 | Each user is saved in its own file, `data/users/<user_id>.json`. The ID is validated before it is used as a file name. | Done |
| USR-06 | In the first version there are no passwords: a profile is created or an existing one is selected. | Planned |
| USR-07 | A user keeps two counters: trips purchased and total amount paid. | Planned |

### 3.4 Purchase (PUR)

| ID | Requirement | Status |
|---|---|---|
| PUR-01 | Only the owner buys a draft trip and pays its full price after discounts. | Planned |
| PUR-02 | The payment is simulated. No payment data is stored. | Planned |
| PUR-03 | A purchase locks the trip, adds one to the trips purchased, adds the amount actually paid to the total paid, awards the points and uses up the points and the voucher that were applied. A rejected purchase changes nothing. | Planned |
| PUR-04 | The first version has no cancellations and no refunds. | Planned |

### 3.5 Points (PNT)

| ID | Requirement | Status |
|---|---|---|
| PNT-01 | Points change only by earning or redeeming. The balance is never negative and invalid amounts are rejected. | Done |
| PNT-02 | The owner earns a fixed number of points for each trip purchased, only if the trip price reaches a minimum. | Planned |
| PNT-03 | A user earns points on their birthday, once per year. The first award comes after the first birthday following registration and it is granted at login. Someone born on 29 February celebrates on 28 February in years that are not leap years. | Planned |
| PNT-04 | A host earns points from the tips received (see TIP-04). | Planned |

### 3.6 Discounts (DSC)

| ID | Requirement | Status |
|---|---|---|
| DSC-01 | When buying a trip, a user can exchange points for a discount: 10 points are 1 %. The user chooses how many points to apply. | Planned |
| DSC-02 | Hosts get an extra 5 % discount on their purchases. | Planned |
| DSC-03 | The total discount of a purchase, adding points, voucher and host discount, never exceeds 30 % of the price. | Planned |
| DSC-04 | Money amounts are rounded to cents. | Planned |

### 3.7 Vouchers (VCH)

| ID | Requirement | Status |
|---|---|---|
| VCH-01 | A user can turn some of their points into a voucher. The points are deducted from the user when the voucher is issued, and the operation is rejected if the balance is not enough. | Planned |
| VCH-02 | A voucher has a code, a value in points and an issue date. It expires seven days after issue and can be used only once. | Planned |
| VCH-03 | The voucher code can be given to anyone, but only a new user can redeem it (no purchases and registered 30 days ago or less). | Planned |
| VCH-04 | A voucher is redeemed when buying a trip and gives the same discount as the same number of points. It counts towards the limit of DSC-03. | Planned |
| VCH-05 | The points of a voucher that expires unused are lost. This pushes users to spend their points soon or to pass them on to a new user. | Planned |

### 3.8 Hosts (HST)

| ID | Requirement | Status |
|---|---|---|
| HST-01 | A user can become a host if they have purchased at least 5 trips, have paid at least 200 € in total (the amount actually paid, after discounts), speak English and apply for their own city only (the one in their profile). | Planned |
| HST-02 | A host profile has a name, a nickname, a city, languages and reviews. | Planned |
| HST-03 | A review has a rating from 1 to 5, a comment and an author. The author must have taken part in the activity. | Planned |
| HST-04 | A host can claim a catalogue activity of their own city that has no host yet. An activity has at most one host and can have none. | Planned |
| HST-05 | Host benefits: the extra discount (DSC-02), the points from tips (TIP-04) and other benefits still to be defined. | Planned |

### 3.9 Tips (TIP)

| ID | Requirement | Status |
|---|---|---|
| TIP-01 | A participant of a purchased trip can give a tip for an activity that has a host and has already taken place. | Planned |
| TIP-02 | A host cannot tip themselves. | Planned |
| TIP-03 | The tip goes to Travel&Go. It does not count towards the 200 € of HST-01, it gives no points to the person who tips and no discount applies to it. | Planned |
| TIP-04 | The host earns one point for every 10 whole euros of the tip. The remainder is lost, so a tip of 9.99 € gives no points. | Planned |
| TIP-05 | Each tip is stored in the file of its trip with its amount, who gave it, the activity and the date. | Planned |

### 3.10 Recommendations (REC)

| ID | Requirement | Status |
|---|---|---|
| REC-01 | The platform suggests activities with simple rules: the kind of activity the user has bought most and the city of their destination. There is no machine learning. | Planned |

### 3.11 Interface (UI)

| ID | Requirement | Status |
|---|---|---|
| UI-01 | A console interface lets the user create or select a profile, build a trip from the catalogue, buy it and, as each feature arrives, use vouchers, hosting and tips. | Planned |
| UI-02 | The profile screen works as the loyalty dashboard: points, trips purchased, total paid and progress towards becoming a host. | Planned |
| UI-03 | The business logic lives in a `services/` package and the console only reads and prints in a `cli/` package, so the console can be replaced by a desktop application. | Planned |
| UI-04 | A graphical interface is to be evaluated. | Planned |

## 4. Configurable values

Every number below lives in one configuration module, so changing a rule never means searching the code.

| Value | Content | Status |
|---|---|---|
| Points per purchased trip | 40 | Agreed |
| Minimum trip price to earn those points | not defined yet | To define |
| Points per birthday | 20 | Agreed |
| Points for a 1 % discount | 10 | Agreed |
| Maximum total discount | 30 % | Agreed |
| Extra discount for hosts | 5 % | Agreed |
| Voucher validity | 7 days | Agreed |
| Maximum age of the registration of a new user | 30 days | Agreed |
| Host requirement: trips purchased | 5 | Agreed |
| Host requirement: total paid | 200 € | Agreed |
| Host requirement: language | `en` | Agreed |
| Euros of tip for one point | 10 | Provisional |
| Rating range of a review | 1 to 5 | Agreed |

*Agreed* values are decisions. *Provisional* ones are a starting point that is expected to change after testing the loyalty system.

## 5. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | At run time the project uses only the Python standard library. `pytest` is a development dependency. |
| NFR-02 | Code, comments, documentation and commits are in English, follow PEP 8 and have type hints on parameters, returns and attributes. |
| NFR-03 | Models never print or read input. All input and output lives in the interface. |
| NFR-04 | A rejected operation does not change the state: data is validated before it is modified. Lists are copied when they enter or leave a class. |
| NFR-05 | Each family of errors has its own base exception, and each exception keeps the value that caused it. |
| NFR-06 | Money is handled with `decimal.Decimal`, not with `float`. |
| NFR-07 | Data files go in `data/` and are ignored by Git. When a field is added to a saved file, the old files still load. |
| NFR-08 | No personal data is used as an identifier, and no passwords are stored in the first version. |
| NFR-09 | Logic that depends on the date (birthdays, voucher expiry, new users, finished activities) receives the current date as a parameter, so it can be tested. |
| NFR-10 | Every feature comes with automated tests. |

## 6. Known limitations

- The payment is simulated, and there are no passwords, cancellations or refunds.
- Participants must be registered users, so children or older people without an account cannot be added as participants.
- Trip IDs are integers assigned by hand until the repository step is done.
- `Trip.load` returns an empty trip when the file does not exist, which can hide errors (see TRP-07).
- `Trip.activities` is a public list that is not copied.
- The `tips_included` field of a guided tour will be removed when tips are implemented, because a tip is a separate payment (see TIP-03).

## 7. Decision log

| # | Decision | Reason |
|---|---|---|
| D1 | The app organises activities only. | Accommodation and transport are out of scope. |
| D2 | To become a host: 5 trips, 200 € paid, own city and English. | Replaces the first proposal of 10 trips and 5 vouchers redeemed. |
| D3 | The 200 € count the amount actually paid. | It reflects real spending and benefits the platform. |
| D4 | A voucher is made of points that are deducted at issue. Points of an expired voucher are lost. | Users are encouraged to spend points soon or to invite new users. |
| D5 | The host extra discount cannot exceed the 30 % limit. | The limit applies to all discounts together. |
| D6 | Tips go to Travel&Go and the host receives points. | Replaces the idea that hosts receive the tips. Points accumulate in the same balance as any user's. |
| D7 | Prices are per person and the owner pays for everyone. | The trip price depends on the number of participants. |
| D8 | A trip is a draft until it is purchased, then it is locked. | The price cannot change after paying. |
| D9 | Activities are created by the platform. | Prevents users from inflating their spending and points. |
| D10 | Simulated payment and profiles without passwords. | The repository is public and the first usable version has to arrive soon. |
| D11 | Recommendations use simple rules. | There is not enough data for anything more complex. |
| D12 | The loyalty dashboard is the profile screen of the console. | One screen less to build. |