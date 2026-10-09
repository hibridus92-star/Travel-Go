# Travel&Go

> A travel management application with a transferable loyalty system and personalised trip recommendations.

**Status:** early development. The repository currently contains the design documentation; the codebase will be added progressively as the project is reorganised into modules.

---

## Overview

Travel&Go helps any traveller, whether travelling alone or with others, find and organise the trip that best fits their needs. It combines activity management, budget tracking and a loyalty system designed to reward both individual and collective use of the platform.

This project is also being developed as my final degree project (TFG) for the Multiplatform Application Development programme (DAM).

## The problem

Planning a trip that mixes several activities, accommodations and providers is usually fragmented across multiple apps and platforms, with no unified view of the budget or of the benefits a frequent traveller has accumulated.

Existing loyalty schemes, such as Booking.com's Genius programme, reward users in isolation: discounts are individual and non-transferable, so they generate no social value and give users no reason to bring others onto the platform.

## Target users

- Solo travellers
- Families
- Groups of friends planning a trip together
- Groups with specific needs, such as senior travel programmes (e.g. IMSERSO)

## What makes it different

- **Transferable rewards.** Discount vouchers and points earned by one user can be passed on to other users, turning loyalty into a social experience and encouraging organic growth.
- **Proactive, personalised recommendations.** The platform suggests trip packages and extras based on each user's history and preferences.
- **A path towards working with the platform.** Long-term users who meet certain requirements can become certified local guides for their own city.

## Current features

The current codebase models trips as a collection of activities organised in a class hierarchy:

- Activity hierarchy (`Activity`, `GuideTour`, `Pubcrawl`) with polymorphic behaviour
- Trip management with total cost calculation
- JSON persistence: trips and their activities can be saved to disk and loaded back, with each activity restored to its correct class
- Custom exceptions for invalid data

## Roadmap

- [x] Core domain model (activities and trips)
- [x] JSON persistence
- [ ] Reorganise the code into modules and packages
- [ ] Discount and points system
- [ ] Voucher transfer between users
- [ ] Loyalty dashboard
- [ ] Trip recommendations
- [ ] Graphical interface (to be evaluated)

## Documentation

- [Class diagram](docs/class_diagram.md): current UML diagram of the domain model

## Tech stack

- Python 3
- PyCharm
- Git and GitHub

## Author

Jose Quintero. Built as a learning project and as a TFG.
