## ADDED Requirements
### Requirement: Position Sizing
The system SHALL provide position sizing algorithms to determine appropriate trade sizes based on account equity, risk tolerance, and strategy parameters.

#### Scenario: Fixed fractional position sizing
- **WHEN** user configures a fixed fractional position sizing method
- **THEN** the system calculates position sizes as a fixed fraction of account equity

#### Scenario: Volatility-adjusted position sizing
- **WHEN** user configures volatility-adjusted position sizing
- **THEN** the system adjusts position sizes inversely to asset volatility

### Requirement: Portfolio Risk Management
The system SHALL provide tools to monitor and manage portfolio-level risk exposure.

#### Scenario: Portfolio risk calculation
- **WHEN** user requests portfolio risk metrics
- **THEN** the system calculates value-at-risk, maximum drawdown, and correlation risk measures

#### Scenario: Risk limit enforcement
- **WHEN** a trade would exceed configured risk limits
- **THEN** the system prevents the trade or reduces position size to comply with limits