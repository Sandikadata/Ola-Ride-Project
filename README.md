# OLA Ride Booking Analysis
Project Overview
This project analyses Ola ride-booking data to understand booking performance, ride value, vehicle usage, cancellations, incomplete rides, and customer/driver ratings. Power BI is used to present the analysis in an interactive dashboard. The wider workflow can include data extraction, transformation, storage, exploratory data analysis (EDA), feature engineering, and statistical testing, depending on the steps implemented in the repository.
Reporting note: The uploaded .pbit file is a Power BI template. The report below documents the project structure and analytical approach; numerical findings should be added only after refreshing the report with the source dataset and validating the measures.

Business Problem
Ride-hailing operations need to understand when bookings occur, which vehicle categories are used, how booking value and distance vary, and where cancellations or incomplete rides affect service delivery. A consolidated dashboard can help stakeholders investigate these questions and identify areas for operational improvement.
Objectives
- Analyse overall booking volume and booking-status distribution.
- Compare vehicle types by booking activity, ride distance, and booking value.
- Explore booking value by payment method and customer.
- Investigate customer- and driver-related cancellations and incomplete rides.
- Review customer and driver ratings as service-quality indicators.
- Use date filters to explore changes across the selected period.
- Support evidence-based operational recommendations.
Tools and Technologies
- Power BI — dashboard development and interactive reporting.
- SQL — querying and analysis, if included in the repository workflow.
- MongoDB — source or staging storage, if used in the implemented pipeline.
- Python / Excel — data inspection or preparation, if used in the project.
Only list tools in the final repository that were actually used. Remove any tool above that is not part of the completed workflow.
Data and Key Fields
The template model contains an OLA_ride table with fields including:
- Booking: Booking_ID, Date, Time, Booking_Status
- Ride: Vehicle_Type, Pickup_Location, Drop_Location, Ride_Distance
- Value and payment: Booking_Value, Payment_Method
- Ratings: Driver_Ratings, Customer_Rating
- Cancellation / incomplete rides: Canceled_Rides_by_Customer, Canceled_Rides_by_Driver, Incomplete_Rides, Incomplete_Rides_Reason
- Turnaround time: V_TAT, C_TAT
Confirm the exact source schema and field names against the supplied dataset before publishing.
Project Workflow
1. Data Extraction, Loading and Transformation (ELT/ETL)
Document how the raw booking data was obtained and loaded. Describe any cleaning or transformation steps actually performed, such as date/time conversion, missing-value treatment, duplicate checks, standardisation of booking statuses, and data-type correction. Use ELT only if data was loaded before transformation; otherwise call the process ETL.
2. MongoDB-to-SQL Migration
If the repository implements this step, describe how records were read from MongoDB, mapped to a relational schema, and loaded into SQL tables. Include table names, key fields, data-type mappings, row-count checks, and validation queries. If this migration was not performed, remove this section rather than implying it was completed.
3. Exploratory Data Analysis (EDA)
Recommended analyses:
- Booking volume by date and booking status.
- Completed, cancelled, and incomplete rides.
- Booking value and ride distance by vehicle type.
- Booking value by payment method.
- Customer- and driver-related cancellations and their recorded reasons.
- Customer and driver rating distributions.
- Turnaround-time patterns using V_TAT and C_TAT, where available.
Add the actual observations from the refreshed dataset here. Do not report a “highest”, “lowest”, trend, or percentage until the chart or query confirms it.
4. Feature Engineering
Potential derived fields include:
- Date parts such as month, weekday, and hour from Date and Time.
- A validated ride outcome category based on Booking_Status.
- Cancellation flags and cancellation reason categories.
- Duration or turnaround-time indicators, if their definitions and units are known.
Document the final features actually created, including formulas and treatment of missing or inconsistent values.
5. Statistical Testing
If a statistical test was performed, specify the business question, null and alternative hypotheses, test selected, significance level, p-value, and conclusion in plain language. Choose a test based on the data and assumptions—for example, a chi-square test for association between categorical variables or a suitable comparison test for numeric groups. Do not claim a test was performed unless code or results are available.
Power BI Dashboard Pages
Page	Purpose
Overall	Booking trend, booking-status distribution, and high-level KPIs.
Vehicle Type	Compare ride distance and booking value across vehicle categories.
Revenue	Explore booking value by payment method/customer and daily ride distance.
Cancellation	Review customer/driver cancellations and related summary indicators.
Ratings	Review customer and driver rating indicators.


Measures and Validation
The template includes measures such as Total Bookings, canceled_booking, and Canceledpercentage. Validate their DAX definitions before publishing results.

A general cancellation-rate formula is:

Cancellation Rate (%) = Cancelled Bookings / Total Bookings × 100

Define exactly which statuses count as cancelled and ensure a booking is not counted twice if customer and driver cancellation flags overlap. Confirm whether rating cards display averages rather than sums, and document the denominator for every percentage.
Business Recommendations
After validating the data, use the findings to consider:
- Investigating the most frequent cancellation reasons and the stages at which cancellations occur.
- Comparing vehicle categories by demand, distance, booking value, and completion rate.
- Reviewing payment-method patterns and booking-value distribution.
- Monitoring rating changes by period and vehicle type.
- Checking turnaround-time patterns for possible service delays.
- Prioritising actions based on measured impact rather than assumptions.
Conclusion
The Power BI template provides a foundation for analysing ride bookings, vehicle categories, booking value, cancellations, and ratings. To make this a strong portfolio project, pair the dashboard with a reproducible data workflow, documented transformations, validated KPI definitions, evidence-based EDA findings, and statistical-test results where applicable.
Repository Checklist
- [ ] Add a clear README with the project objective and workflow.
- [ ] Include screenshots of each dashboard page.
- [ ] Explain the source dataset and any usage restrictions.
- [ ] Document data cleaning, SQL/MongoDB steps, and feature engineering only if implemented.
- [ ] Add SQL queries, Python notebooks/scripts, and statistical test output where applicable.
- [ ] Validate all KPI definitions and add actual findings.
- [ ] Avoid uploading credentials, private data, or files you are not authorised to share.
