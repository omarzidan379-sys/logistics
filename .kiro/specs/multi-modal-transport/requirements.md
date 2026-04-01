# Requirements Document

## Introduction

This document specifies the requirements for adding Multi-Modal Transport capability to the Odoo 17 Freight Management System. The feature enables handling of complex shipments that traverse multiple transport legs using different transport modes (Sea, Air, Road, Rail). This addresses a critical gap in the current system which only supports single-leg shipments, preventing it from handling real-world international logistics scenarios where cargo typically transfers between multiple carriers and transport modes.

## Glossary

- **Multi_Modal_Transport_System**: The extended freight management system that handles shipments with multiple transport legs
- **Transport_Leg**: A single segment of a multi-modal journey with one transport mode, origin, destination, and carrier
- **Leg_Manager**: The component responsible for creating, updating, and tracking individual transport legs
- **Route_Optimizer**: The component that suggests optimal routes based on cost, time, and other factors
- **Transshipment_Point**: A location where cargo transfers from one transport mode to another
- **Intermodal_Container**: A container designed to move across multiple transport modes without unloading cargo
- **Leg_Milestone**: A tracking event specific to an individual transport leg
- **Delay_Propagator**: The component that calculates impact of delays in one leg on subsequent legs
- **Cost_Aggregator**: The component that calculates total costs across all transport legs
- **Transit_Time_Calculator**: The component that calculates total journey time across all legs
- **Shipment**: The existing freight.shipment model representing a freight movement
- **Container**: The existing freight.container model for container tracking
- **Location**: The existing freight.location model for ports, airports, and warehouses
- **Booking**: The existing freight.booking model for booking management
- **Quotation**: The existing freight.quotation model for pricing

## Requirements

### Requirement 1: Multi-Leg Shipment Support

**User Story:** As a freight forwarder, I want to create shipments with multiple transport legs, so that I can handle complex international routes that require different transport modes.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL support shipments with a minimum of 1 transport leg and a maximum of 20 transport legs
2. WHEN a user creates a new shipment, THE Multi_Modal_Transport_System SHALL allow the user to add multiple transport legs
3. WHEN a user adds a transport leg, THE Leg_Manager SHALL require origin location, destination location, transport mode, and sequence number
4. THE Multi_Modal_Transport_System SHALL maintain backward compatibility with existing single-leg shipments
5. WHEN a shipment has multiple legs, THE Multi_Modal_Transport_System SHALL validate that the destination of leg N matches the origin of leg N+1

### Requirement 2: Transport Leg Data Management

**User Story:** As a logistics coordinator, I want each transport leg to have its own detailed information, so that I can track and manage each segment independently.

#### Acceptance Criteria

1. THE Leg_Manager SHALL store transport mode for each leg with values Sea, Air, Road, or Rail
2. THE Leg_Manager SHALL store origin location and destination location for each leg
3. THE Leg_Manager SHALL store carrier information for each leg
4. THE Leg_Manager SHALL store estimated departure date and estimated arrival date for each leg
5. THE Leg_Manager SHALL store actual departure date and actual arrival date for each leg
6. THE Leg_Manager SHALL store cost breakdown for each leg including freight charges, fuel surcharges, and handling fees
7. THE Leg_Manager SHALL store status for each leg with values Draft, Booked, In_Transit, Completed, or Cancelled
8. THE Leg_Manager SHALL store leg sequence number to maintain order of legs
9. THE Leg_Manager SHALL store vessel name, voyage number, or flight number for each leg
10. THE Leg_Manager SHALL store booking reference for each leg

### Requirement 3: Transshipment Point Management

**User Story:** As a freight forwarder, I want to identify and manage transshipment points, so that I can track where cargo transfers between transport modes.

#### Acceptance Criteria

1. WHEN a location serves as both destination of one leg and origin of the next leg, THE Multi_Modal_Transport_System SHALL identify it as a transshipment point
2. THE Multi_Modal_Transport_System SHALL display all transshipment points for a shipment in sequence order
3. THE Multi_Modal_Transport_System SHALL store handling time at each transshipment point
4. THE Multi_Modal_Transport_System SHALL store handling cost at each transshipment point
5. WHEN cargo arrives at a transshipment point, THE Multi_Modal_Transport_System SHALL track the transfer status with values Pending, In_Progress, or Completed

### Requirement 4: Transit Time Calculation

**User Story:** As a customer service representative, I want to see total transit time across all legs, so that I can provide accurate delivery estimates to customers.

#### Acceptance Criteria

1. THE Transit_Time_Calculator SHALL calculate total estimated transit time by summing estimated duration of all legs plus handling time at transshipment points
2. THE Transit_Time_Calculator SHALL calculate total actual transit time by summing actual duration of all completed legs plus actual handling time at transshipment points
3. WHEN estimated dates change for any leg, THE Transit_Time_Calculator SHALL recalculate total estimated transit time within 1 second
4. THE Transit_Time_Calculator SHALL display transit time in days and hours format
5. THE Transit_Time_Calculator SHALL calculate variance between estimated and actual transit time

### Requirement 5: Independent Leg Status Tracking

**User Story:** As a logistics coordinator, I want to track each leg independently with its own milestones, so that I can monitor progress at a granular level.

#### Acceptance Criteria

1. THE Leg_Manager SHALL track status for each leg independently of other legs
2. THE Leg_Manager SHALL support leg-specific milestones including Booking_Confirmed, Cargo_Loaded, Departed, In_Transit, Arrived, and Cargo_Discharged
3. WHEN a milestone is reached for a leg, THE Leg_Manager SHALL record the timestamp
4. THE Multi_Modal_Transport_System SHALL display milestone progress for each leg separately
5. WHEN all legs reach Completed status, THE Multi_Modal_Transport_System SHALL update the shipment status to Completed

### Requirement 6: Intermodal Container Support

**User Story:** As a freight forwarder, I want to track containers that move across multiple transport modes, so that I can maintain container visibility throughout the journey.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL allow associating a container with multiple transport legs
2. WHEN a container is assigned to a leg, THE Multi_Modal_Transport_System SHALL validate that the container transport mode compatibility
3. THE Multi_Modal_Transport_System SHALL track which legs a container traverses
4. THE Multi_Modal_Transport_System SHALL maintain container seal number across all legs
5. WHEN a container transfers between legs, THE Multi_Modal_Transport_System SHALL record the transfer timestamp and location

### Requirement 7: Cost Aggregation

**User Story:** As a finance manager, I want to see total costs aggregated across all legs, so that I can understand the complete shipment cost.

#### Acceptance Criteria

1. THE Cost_Aggregator SHALL calculate total estimated cost by summing estimated costs of all legs plus transshipment handling costs
2. THE Cost_Aggregator SHALL calculate total actual cost by summing actual costs of all legs plus actual transshipment handling costs
3. THE Cost_Aggregator SHALL display cost breakdown by leg showing each leg contribution to total cost
4. THE Cost_Aggregator SHALL display cost breakdown by charge type showing freight, surcharges, and handling fees across all legs
5. THE Cost_Aggregator SHALL calculate cost variance between estimated and actual costs
6. WHEN costs change for any leg, THE Cost_Aggregator SHALL recalculate total costs within 1 second

### Requirement 8: Route Optimization Suggestions

**User Story:** As a freight forwarder, I want to receive route optimization suggestions, so that I can select the most efficient multi-modal route.

#### Acceptance Criteria

1. WHEN a user specifies origin and destination, THE Route_Optimizer SHALL suggest at least 3 alternative multi-modal routes
2. THE Route_Optimizer SHALL calculate estimated cost for each suggested route
3. THE Route_Optimizer SHALL calculate estimated transit time for each suggested route
4. THE Route_Optimizer SHALL rank suggested routes by cost, time, or balanced score
5. THE Route_Optimizer SHALL consider available carriers and their schedules when suggesting routes
6. WHERE route optimization is enabled, THE Route_Optimizer SHALL highlight the recommended route based on user preferences

### Requirement 9: Delay Impact Propagation

**User Story:** As a logistics coordinator, I want to see how delays in one leg affect subsequent legs, so that I can proactively manage customer expectations and rebook connections.

#### Acceptance Criteria

1. WHEN actual departure or arrival time for a leg differs from estimated time by more than 2 hours, THE Delay_Propagator SHALL identify it as a delay
2. WHEN a delay occurs in leg N, THE Delay_Propagator SHALL calculate impact on estimated departure time of leg N+1
3. WHEN a delay causes a missed connection, THE Delay_Propagator SHALL flag the affected legs with status Connection_At_Risk
4. THE Delay_Propagator SHALL calculate revised estimated arrival time for the final destination considering all delays
5. WHEN a delay is detected, THE Multi_Modal_Transport_System SHALL send notification to the responsible user
6. THE Delay_Propagator SHALL display delay duration and affected legs in the shipment view

### Requirement 10: Leg-Specific Document Management

**User Story:** As a documentation specialist, I want to attach documents to specific transport legs, so that I can organize paperwork by leg and transport mode.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL allow attaching documents to individual transport legs
2. THE Multi_Modal_Transport_System SHALL support document types including Bill_of_Lading, Air_Waybill, CMR, Customs_Declaration, and Packing_List
3. WHEN a document is attached to a leg, THE Multi_Modal_Transport_System SHALL store document type, upload date, and uploaded by user
4. THE Multi_Modal_Transport_System SHALL display all documents grouped by leg
5. THE Multi_Modal_Transport_System SHALL allow downloading documents for a specific leg or all legs
6. THE Multi_Modal_Transport_System SHALL validate that required documents are attached before a leg can be marked as Completed

### Requirement 11: Quotation Integration

**User Story:** As a sales representative, I want to create quotations for multi-modal shipments, so that I can provide accurate pricing for complex routes.

#### Acceptance Criteria

1. WHEN creating a quotation, THE Multi_Modal_Transport_System SHALL allow specifying multiple transport legs with pricing for each leg
2. THE Multi_Modal_Transport_System SHALL calculate total quotation amount by summing leg costs and transshipment costs
3. WHEN a quotation is approved, THE Multi_Modal_Transport_System SHALL allow creating a booking that preserves the multi-leg structure
4. THE Multi_Modal_Transport_System SHALL display leg-by-leg pricing breakdown in the quotation PDF report
5. THE Multi_Modal_Transport_System SHALL support applying discounts at leg level or total shipment level

### Requirement 12: Booking Integration

**User Story:** As a booking agent, I want to create bookings for multi-modal shipments, so that I can reserve capacity across multiple carriers.

#### Acceptance Criteria

1. WHEN creating a booking from a multi-leg quotation, THE Multi_Modal_Transport_System SHALL create booking records for each leg
2. THE Multi_Modal_Transport_System SHALL allow specifying different carriers for different legs
3. THE Multi_Modal_Transport_System SHALL track booking confirmation status for each leg independently
4. WHEN all leg bookings are confirmed, THE Multi_Modal_Transport_System SHALL update the shipment booking status to Fully_Confirmed
5. IF any leg booking is cancelled, THEN THE Multi_Modal_Transport_System SHALL flag the shipment with status Booking_Incomplete

### Requirement 13: Container Assignment Across Legs

**User Story:** As a container coordinator, I want to assign containers to specific legs, so that I can track which containers are used for which transport segments.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL allow assigning containers to one or more transport legs
2. WHEN a container is assigned to multiple legs, THE Multi_Modal_Transport_System SHALL validate that the legs are consecutive
3. THE Multi_Modal_Transport_System SHALL display which containers are active for each leg
4. WHEN cargo is transferred between containers at a transshipment point, THE Multi_Modal_Transport_System SHALL record the container change
5. THE Multi_Modal_Transport_System SHALL calculate demurrage and detention separately for each leg where a container is used

### Requirement 14: Reporting and Analytics

**User Story:** As a operations manager, I want to generate reports on multi-modal shipments, so that I can analyze performance and identify bottlenecks.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL generate reports showing average transit time by route and transport mode combination
2. THE Multi_Modal_Transport_System SHALL generate reports showing cost breakdown by leg and transport mode
3. THE Multi_Modal_Transport_System SHALL generate reports showing on-time performance by leg and carrier
4. THE Multi_Modal_Transport_System SHALL generate reports showing most frequently used transshipment points
5. THE Multi_Modal_Transport_System SHALL generate reports showing delay frequency and average delay duration by leg

### Requirement 15: User Interface for Multi-Leg Management

**User Story:** As a freight forwarder, I want an intuitive interface to manage multi-leg shipments, so that I can efficiently create and monitor complex routes.

#### Acceptance Criteria

1. THE Multi_Modal_Transport_System SHALL display all transport legs in a sequential list view showing leg number, mode, route, and status
2. THE Multi_Modal_Transport_System SHALL provide a visual timeline showing all legs and transshipment points
3. THE Multi_Modal_Transport_System SHALL allow adding, editing, and removing legs from the shipment form
4. THE Multi_Modal_Transport_System SHALL display a route map showing all legs and transshipment points with different colors for different transport modes
5. WHEN a user clicks on a leg, THE Multi_Modal_Transport_System SHALL display detailed leg information in an expandable panel
6. THE Multi_Modal_Transport_System SHALL provide a button to duplicate a leg for creating similar legs quickly
