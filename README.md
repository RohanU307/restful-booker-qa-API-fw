# Restful Booker API – Quality Assurance Automation Framework

## 1. Project Overview

This project implements an automated API testing framework for the Restful Booker public demo API as part of the **Senior Engineer – Technology Quality Assurance Assessment**.

The framework focuses on API reliability, authentication and token lifecycle management, booking data validation, update semantics, concurrent requests, and recovery from missing resources.

It uses Python and pytest to execute automated tests and generate an HTML test report.

**Target API:** `https://restful-booker.herokuapp.com`

### Key Objectives

* Validate booking creation, retrieval, updating, and deletion.
* Implement token caching, expiration handling, and authentication recovery.
* Validate booking payloads and date invariants.
* Test PUT idempotency and PATCH field preservation.
* Investigate concurrent updates to the same booking.
* Examine duplicate booking behavior in the public sandbox.
* Recover from missing bookings during test execution.
* Generate test execution reports for assessment and review.

---

## 2. Technology Stack

| Technology         | Purpose                                  |
| ------------------ | ---------------------------------------- |
| Python             | Test framework implementation            |
| pytest             | Test execution, assertions, and fixtures |
| Requests           | HTTP requests and API communication      |
| jsonschema         | Booking payload schema validation        |
| pytest-html        | HTML test report generation              |
| ThreadPoolExecutor | Concurrent request execution             |
| threading.Barrier  | Coordinating concurrent test requests    |
| PyCharm            | Development environment                  |

---

## 3. Project Structure

The project is organized into reusable API client, authentication, test data, validation, recovery, and test modules.

```text
restful_booker_qa_framework/
│
├── api_client.py
├── auth_manager.py
├── config.py
├── conftest.py
├── data_factory.py
├── schemas.py
├── recovery.py
│
├── tests/
│   ├── test_api_client_auth.py
│   ├── test_auth_manager.py
│   ├── test_booking_lifecycle.py
│   ├── test_concurrency.py
│   ├── test_dates_and_duplicate.py
│   ├── test_recovery.py
│   ├── test_update_recovery.py
│   └── test_updates.py
│
├── requirements.txt
├── pytest.ini
├── README.md
└── report.html
```

**Note:** `report.html` is generated after running the HTML reporting command. Depending on your local setup, it may not exist until you generate it.

### Module Responsibilities

| Module             | Responsibility                                                             |
| ------------------ | -------------------------------------------------------------------------- |
| `config.py`        | API base URL and request timeout configuration                             |
| `auth_manager.py`  | Token caching, token expiration, refresh, and thread-safe token generation |
| `api_client.py`    | HTTP methods, authenticated requests, and authentication retry handling    |
| `data_factory.py`  | Dynamic booking payload generation and booking creation                    |
| `schemas.py`       | Booking schema and business-invariant validation                           |
| `conftest.py`      | Shared pytest fixtures and booking lifecycle setup/teardown                |
| `recovery.py`      | Recovery when a booking is missing during a test or update                 |
| `tests/`           | Automated API tests                                                        |
| `pytest.ini`       | pytest configuration                                                       |
| `requirements.txt` | Python dependencies                                                        |
| `report.html`      | Generated HTML test execution report                                       |

---

## 4. Prerequisites

Install the following before running the framework:

* Python 3.10 or later
* pip
* PyCharm or another Python IDE
* Internet access to reach the Restful Booker public demo API

The framework has been executed successfully in a Python 3.14.7 environment.

The public API is a shared demonstration environment. Its availability, data, and behavior may vary between test executions.

---

## 5. Installation and Setup

### Step 1: Open the Project

Open the project root directory in PyCharm.

Example Windows path:

```text
D:\restful_booker_qa_framework\restful_booker_qa_framework
```

### Step 2: Create a Virtual Environment

If a virtual environment has not already been created, execute:

```bash
python -m venv .venv
```

Activate it in Windows Command Prompt:

```bat
.venv\Scripts\activate
```

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PyCharm already has the correct virtual environment configured, you can use the existing environment.

### Step 3: Install Dependencies

Run:

```bash
python -m pip install -r requirements.txt
```

The project dependencies include:

* `requests`
* `pytest`
* `jsonschema`
* `pytest-html`

### Step 4: Verify the API Configuration

The default configuration in `config.py` is:

```python
import os

BASE_URL = os.getenv(
    "BASE_URL",
    "https://restful-booker.herokuapp.com"
).rstrip("/")

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "10")
)
```

The API URL and timeout can be overridden using environment variables.

Windows Command Prompt:

```bat
set BASE_URL=https://restful-booker.herokuapp.com
set REQUEST_TIMEOUT_SECONDS=10
```

PowerShell:

```powershell
$env:BASE_URL = "https://restful-booker.herokuapp.com"
$env:REQUEST_TIMEOUT_SECONDS = "10"
```

---

## 6. Running the Tests

Run commands from the project root directory.

### Run the Complete Test Suite

```bash
python -m pytest -v
```

This runs all discovered tests and displays individual test results.

### Run Tests with Detailed Output

```bash
python -m pytest -v -s
```

The `-s` option displays print statements, including diagnostic messages and observed sandbox behavior.

### Run Authentication Tests

```bash
python -m pytest -v tests/test_auth_manager.py tests/test_api_client_auth.py
```

### Run Booking Lifecycle Tests

```bash
python -m pytest -v tests/test_booking_lifecycle.py
```

### Run Date and Duplicate Booking Tests

```bash
python -m pytest -v -s tests/test_dates_and_duplicate.py
```

### Run Concurrent Update Tests

```bash
python -m pytest -v -s tests/test_concurrency.py
```

### Run PUT and PATCH Tests

```bash
python -m pytest -v tests/test_updates.py
```

### Run Recovery Tests

```bash
python -m pytest -v tests/test_recovery.py tests/test_update_recovery.py
```

---

## 7. HTML Test Report

The framework uses `pytest-html` to generate a standalone HTML test report.

Execute:

```bash
python -m pytest -v --html=report.html --self-contained-html
```

The generated file is:

```text
report.html
```

Open `report.html` in a web browser to review the execution summary, individual test results, and failure details, if any.

The `--self-contained-html` option makes the report suitable for sharing without requiring separate report assets.

**Important:** The report is generated from the latest test execution. Review its results before submitting it.

---

## 8. Implemented Test Scenarios

### 8.1 Authentication and Token Lifecycle

**Test modules:**

* `tests/test_auth_manager.py`
* `tests/test_api_client_auth.py`

The tests cover:

* Reusing a cached authentication token.
* Generating a token when no usable token is available.
* Regenerating an invalidated or expired cached token.
* Coordinating concurrent token generation.
* Reusing a newly refreshed token when simultaneous requests encounter an authentication failure.
* Refreshing authentication after HTTP 401.
* Refreshing authentication after HTTP 403.
* Limiting authentication recovery to a single retry.

The authentication manager uses a configurable local token-cache lifetime.

The default cache lifetime is five minutes. This is a client-side caching policy and should not be interpreted as a verified server-side token expiration time.

**Important distinction:** The authentication unit tests use mocked responses for relevant scenarios. Passing these tests verifies the implemented client behavior under the tested conditions; it does not prove that the live server expires tokens according to the local cache lifetime.

### 8.2 Booking Creation and Retrieval

**Test module:** `tests/test_booking_lifecycle.py`

The tests cover:

* Creating a booking.
* Extracting the booking ID from the creation response.
* Retrieving the created booking.
* Validating the returned booking information.
* Handling a booking ID that does not exist.

### 8.3 Schema and Date Validation

**Test module:** `tests/test_dates_and_duplicate.py`

The framework generates booking dates programmatically rather than relying on hard-coded dates.

The validation checks include:

* Required booking fields.
* First name and last name data types.
* Non-negative integer booking price.
* Boolean deposit-paid flag.
* Nested booking date fields.
* ISO-format calendar dates.
* Checkout date occurring after check-in date.

These checks help identify malformed responses and violations of booking data invariants.

### 8.4 Duplicate Booking Behavior

**Test module:** `tests/test_dates_and_duplicate.py`

The framework creates bookings with identical date ranges to investigate whether the public sandbox rejects overlapping bookings.

In the observed test executions, the sandbox returned HTTP 200 and generated separate booking IDs for duplicate date ranges.

The tests recorded this behavior and attempted to remove the created test bookings.

**Finding:** The tested API accepted duplicate date-range bookings. No room-level date-conflict validation was observed during these requests.

This finding describes the behavior of the public sandbox under the tested conditions. It does not establish how a production reservation system should behave or whether the sandbox supports room availability management.

### 8.5 PUT Idempotency

**Test module:** `tests/test_updates.py`

The test sends the same PUT payload three times to the same booking.

It verifies that:

* The requests succeed under the tested conditions.
* The returned booking representation remains stable across repeated updates.
* The final persisted booking matches the intended payload.

This tests the expected idempotent behavior of repeated PUT operations for the tested booking.

### 8.6 PATCH Field Preservation

**Test module:** `tests/test_updates.py`

The test updates a single field using PATCH.

It verifies that:

* The requested field is changed.
* Other booking fields remain unchanged.
* The final persisted booking matches the expected state.

This helps detect accidental changes to fields that were not part of the partial update.

### 8.7 Concurrent Updates

**Test module:** `tests/test_concurrency.py`

The framework submits two conflicting updates to the same booking using a thread pool and a synchronization barrier.

The test captures:

* Client-side request initiation timestamps.
* HTTP status codes.
* Response bodies.
* The final persisted booking.
* Schema validity of the final state.

In an observed execution:

* Both updates returned HTTP 200.
* The client-side initiation timestamps were approximately 0.533 milliseconds apart.
* The final persisted booking matched one of the two complete submitted payloads.

**Interpretation:** The observed final state matched one complete update, rather than a mixture of the two test payloads.

The timestamps represent client-side request initiation, not the exact time the server received or processed each request. This test does not establish a guaranteed conflict-resolution policy, strict ordering, or atomicity under every concurrent workload.

### 8.8 Recovery from Missing Bookings

**Test modules:**

* `tests/test_recovery.py`
* `tests/test_update_recovery.py`

The recovery logic handles situations where a booking required by a test no longer exists.

The implemented behavior includes:

* Checking whether the booking exists.
* Recreating the prerequisite booking when the API returns HTTP 404.
* Retrying an update against the replacement booking when the original booking disappears during the update.
* Reporting unexpected HTTP responses instead of treating every error as a missing resource.

This is particularly relevant to a public sandbox where test data may be deleted or modified by other users.

---

## 9. Authentication and Request Flow

The authentication-enabled request flow is designed as follows:

1. The API client requests a usable token from the authentication manager.
2. The authentication manager returns the cached token when it is still valid according to the configured cache policy.
3. If no usable token is available, a new token is requested.
4. The API client sends the request with the authentication cookie.
5. If the response is HTTP 401 or 403, the client attempts to refresh or reuse a newer token.
6. The original request is retried once.
7. The final response is returned to the caller.

The single-retry limit prevents unbounded authentication retry loops.

HTTP 403 does not always mean that a token has expired. It may also indicate insufficient permissions or another authorization restriction. Consequently, the framework returns the final response if the retry does not resolve the problem.

---

## 10. Test Data Management and Cleanup

The framework generates booking payloads dynamically.

Generated data includes:

* Unique test names.
* Programmatically calculated check-in and checkout dates.
* Booking price.
* Deposit-paid status.
* Additional booking requirements.

Dynamic test data reduces collisions between repeated test runs.

Where tests create bookings in the public sandbox, cleanup is attempted to reduce residual test data.

However, the public API is shared and network requests may fail intermittently. A cleanup request can fail because of a transient connection problem, and cleanup is not guaranteed to succeed in every execution.

When cleanup fails, the test output should clearly distinguish the cleanup problem from the main test result.

---

## 11. Observed Test Results

The complete test suite has been executed successfully in the current development environment.

| Test Area                                      |  Tests |
| ---------------------------------------------- | -----: |
| API client authentication recovery             |      3 |
| Authentication manager                         |      5 |
| Booking lifecycle                              |      2 |
| Concurrent updates                             |      1 |
| Date validation and duplicate booking behavior |      3 |
| Missing-booking recovery                       |      1 |
| Update recovery                                |      1 |
| PUT and PATCH behavior                         |      2 |
| **Total**                                      | **18** |

**Observed result: 18 passed in 25.91 seconds.**

This result represents the recorded execution in the current environment. Results may vary when the shared public API is unavailable, behaves differently, or is modified by other users.

Run the suite again before submitting the final report to ensure that the current code and generated report reflect the same execution.

---

## 12. Known Limitations

1. **Shared public sandbox:** Other users can create, update, or delete bookings during test execution.
2. **Network instability:** Requests may fail because of timeouts, connection resets, or temporary API unavailability.
3. **Token expiration assumptions:** The configured token-cache lifetime is a client-side policy, not a confirmed server-side expiry duration.
4. **Duplicate booking validation:** Duplicate date ranges were accepted in the observed executions. The public API's tested behavior should not be generalized to production booking systems.
5. **Concurrency guarantees:** The concurrency test records observed outcomes but does not prove a universal server-side ordering or conflict-resolution policy.
6. **Cleanup:** Best-effort cleanup cannot guarantee removal of all test records if the public API is temporarily unavailable.

---

## 13. Potential Future Improvements

The framework could be extended with:

* GitHub Actions or another CI/CD pipeline.
* Structured logging instead of relying primarily on print statements.
* Configurable retry policies for transient network errors.
* Additional negative tests for malformed payloads and invalid field values.
* More extensive concurrent update tests.
* Test coverage and static analysis reporting.
* A dedicated test environment with controlled data and predictable behavior.
* Environment-based configuration for credentials and other sensitive values.
* Explicit cleanup reporting and improved cleanup retries.

These are potential enhancements and should not be interpreted as already implemented unless they are present in the project.

---

## 14. Conclusion

This project demonstrates an API quality assurance approach using Python, pytest, and Requests.

It covers authentication recovery, booking lifecycle operations, schema and date validation, duplicate booking investigation, PUT and PATCH behavior, concurrent updates, and recovery from missing resources.

The test suite recorded **18 passing tests** in the current development environment.

The generated HTML report provides a reviewable summary of the test execution, while the observed sandbox behavior and known limitations are documented to distinguish verified test results from assumptions about the underlying API.

**Project:** Restful Booker API – Quality Assurance Automation Framework
**Assessment:** Senior Engineer – Technology Quality Assurance
**Test framework:** Python + pytest
**Report format:** Standalone HTML


## GitHub Actions CI Pipeline

This project uses GitHub Actions to automate API test execution.

### Workflow Triggers

The workflow runs on:

* Pushes to the `main` or `master` branch.
* Pull requests targeting the `main` or `master` branch.
* Manual execution through GitHub Actions.

### Pipeline Steps

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Runs the complete pytest suite.
5. Generates a self-contained HTML test report.
6. Uploads the report as a workflow artifact.

### Viewing Test Results

To review a workflow execution:

1. Open the repository on GitHub.
2. Select the **Actions** tab.
3. Open the relevant workflow run.
4. Review the pytest output.
5. Download the `restful-booker-pytest-report` artifact.

The report artifact is retained for 14 days.

### Running the Pipeline Locally

The equivalent local test command is:

```bash
python -m pytest -v --html=report.html --self-contained-html
```

The CI pipeline runs tests against the public Restful Booker demo API. Because the API is shared and externally hosted, transient network failures or changes to sandbox state can affect individual runs.
