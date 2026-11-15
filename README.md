# Travel&Go

> A travel activity planner with a transferable loyalty system and personalised activity recommendations.

**Status:** early development. The core domain model (activities, trips and users with a travel points balance) is implemented and covered by automated tests. The loyalty features are being added step by step.
---

## Overview

Travel&Go helps any traveller, whether travelling alone or with others, plan what to do on a trip once the destination and the length of the stay are already decided. It combines activity management, budget tracking and a loyalty system designed to reward both individual and collective use of the platform.

This project is also being developed as my final degree project (TFG) for the Multiplatform Application Development programme (DAM).

## Scope

Travel&Go organises the **activities** of a trip: guided tours, pub crawls and similar plans. The user chooses the destination and how long to stay there, and the app helps plan what to do during that time, keeping track of the total cost.

It does **not** handle accommodation or transport.

## The problem

Once the destination is chosen, planning what to do there is usually fragmented across multiple apps and providers, with no unified view of the activities' budget or of the benefits a frequent traveller has accumulated.

Existing loyalty schemes, such as Booking.com's Genius programme, reward users in isolation: discounts are individual and non-transferable, so they generate no social value and give users no reason to bring others onto the platform.

## Target users

- Solo travellers
- Families
- Groups of friends planning the activities of a trip together
- Groups with specific needs, such as seniors travelling together who want a ready-made plan of activities at their destination

## What makes it different

- **Transferable rewards.** Points earned by a user can be turned into a discount voucher and passed on to a new user. The points are deducted from the user who gives the voucher away, which turns loyalty into a social experience and encourages organic growth.
- **Proactive, personalised recommendations.** The platform suggests activity packages and extras based on each user's history and preferences.
- **A path towards working with the platform.** Users who have bought enough trips and spent enough on them can become certified local guides, called hosts, for their own city. Hosts get extra discounts and other benefits.

## How the loyalty system works

1. **Earn points.** Users earn points when they buy a trip (that is, its set of activities) and on their birthday. Hosts also earn points for taking part in activities.
2. **Spend points.** Points are exchanged for discounts when buying a trip.
3. **Share.** A user can turn part of their points into a voucher and give it to a new user to invite them to the platform. The voucher can be used only once and expires after a short time. Points that go unused in an expired voucher are lost.
4. **Become a host.** A user who has bought a minimum number of trips and spent a minimum amount on them can become a host for their own city, as long as English is among the languages they speak. Hosts get extra discounts and other benefits.

The exact amounts (points per action, discount rates and host requirements) are still being defined and are not fixed in this document.

## Current features

The current codebase models trips, activities and users:

- Activity hierarchy (`Activity`, `GuideTour`, `Pubcrawl`) with polymorphic behaviour
- Trip management with total cost calculation
- Trip participants, stored as user IDs, with duplicates and unknown participants rejected
- Users with a unique ID, an age calculated from their birth date and a travel points balance that can only change by earning or redeeming points
- JSON persistence: trips and their activities, with each activity restored to its correct class, and one file per user
- Custom exceptions for invalid data
- Automated tests with `pytest`

## Roadmap

- [x] Core domain model (activities, trips and users)
- [x] JSON persistence
- [x] Reorganise the code into modules and packages
- [x] Automated tests with pytest
- [ ] Discount and points system
- [ ] Voucher transfer between users
- [ ] Host profiles
- [ ] Loyalty dashboard
- [ ] Activity recommendations
- [ ] Console interface
- [ ] Graphical interface (to be evaluated)

## Documentation

- [Class diagram](docs/class_diagram.md): current UML diagram of the domain model

## Running the tests

The project has no runtime dependencies. To run the automated tests, install the development dependencies and run `pytest` from the repository root:

```
pip install -r requirements-dev.txt
pytest
```

The tests live in the `tests/` folder. Any files they write go to temporary folders, so the `data/` folder is never touched.

## Tech stack

- Python 3
- PyCharm
- Git and GitHub
- pytest (development only

## Author

Jose Quintero. Built as a learning project and as a TFG.




