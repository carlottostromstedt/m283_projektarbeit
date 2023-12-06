## Introduction

For the course 183 i created a full-stack application in flask. This application consists of a classic html/css/javascript frontend and a python backend connected to a sqlite database.

This course focuses on and we were introduced to multiple tools for scanning existing applications for security vulnerabilities. Using these tools i want to improve the security of my existing full-stack application.

## Scanning for vulnerabilities

To scan for these vulnerabilities i used Zed Attack Proxy (ZAP) which they themselves call:

>The world’s most widely used web app scanner. Free and open source. Actively maintained by a dedicated international team of volunteers. A GitHub Top 1000 project. 

The application has different modes for scanning. I used the automatic mode which prompts for the url of the web application.
#### Session Authentication

To allow the scan to also post correct information during login / authentication we can add the login target url (POST) and the URL to GET Login page to our context under session properties. In my case these are on the surl.

![Session Properties](assets/session_properties.png)

We can then also add a User with correct credentials to be used when accessing the login page during our scan.

![User Properties](assets/user_properties.png)

### Scan

The scan is then done automatically and the submitted requests are shown under *Active scan*

![Active Scan](assets/active_scan.png)

### Scan results

I let ZAP output the results into an HTML report. I then used ChatGPT to summarise this report:

### Summary of ZAP Scanning Report

#### Report Details
- **ZAP Version:** 2.14.0
- **Generated:** Wed 6 Dec 2023, at 09:50:17

#### About this Report
- **Contexts:** All contexts included
- **Sites:** Included site - [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Risk Levels Included:** High, Medium, Low, Informational
- **Confidence Levels Included:** User Confirmed, High, Medium, Low
- **Exclusions:** None

#### Summaries
- **Alert Counts by Risk and Confidence:**
  - High-Risk Alerts: 3 (27.3%)
  - Medium-Risk Alerts: 6 (54.5%)
  - Low-Risk Alerts: 2 (18.2%)
  - Informational-Risk Alerts: 0 (0.0%)

- **Alert Counts by Site and Risk:**
  - [http://127.0.0.1:5000](http://127.0.0.1:5000)
    - High Risk: 2 alerts
    - Medium Risk: 3 alerts
    - Low Risk: 4 alerts
    - Informational: 2 alerts

- **Alert Counts by Alert Type and Risk:**
  - Path Traversal: 1 (High Risk - 9.1%)
  - SQL Injection: 1 (High Risk - 9.1%)
  - Absence of Anti-CSRF Tokens: 3 (Medium Risk - 27.3%)
  - Content Security Policy (CSP) Header Not Set: 8 (Medium Risk - 72.7%)
  - Missing Anti-clickjacking Header: 5 (Medium Risk - 45.5%)
  - Application Error Disclosure: 1 (Low Risk - 9.1%)
  - Information Disclosure - Debug Error Messages: 1 (Low Risk - 9.1%)
  - Server Leaks Version Information via "Server" HTTP Response Header Field: 12 (Low Risk - 109.1%)
  - X-Content-Type-Options Header Missing: 9 (Low Risk - 81.8%)
  - GET for POST: 1 (Informational Risk - 9.1%)
  - Information Disclosure - Suspicious Comments: 1 (Informational Risk - 9.1%)

#### Alerts Details
- **High Risk, Medium Confidence:** 1 alert - SQL Injection at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
- **High Risk, Low Confidence:** 1 alert - Path Traversal at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
- **Medium Risk, High Confidence:** 1 alert - CSP Header Not Set at [http://127.0.0.1:5000/sitemap.xml](http://127.0.0.1:5000/sitemap.xml)
- **Medium Risk, Medium Confidence:** 
  - Absence of Anti-CSRF Tokens
  - Missing Anti-clickjacking Header
  - Server Leaks Version Information via "Server" HTTP Response Header Field
- **Low Risk, High Confidence:** 
  - Application Error Disclosure at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
  - Information Disclosure - Debug Error Messages at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
  - X-Content-Type-Options Header Missing at [http://127.0.0.1:5000/static/css/styles.css](http://127.0.0.1:5000/static/css/styles.css)
  - Information Disclosure - Suspicious Comments at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
- **Informational Risk, High Confidence:** 
  - GET for POST at [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
- **Informational Risk, Medium Confidence:** 
  - Information Disclosure - Suspicious Comments at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)

## Solutions for Vulnerabilities

### SQL Injection

SQL Injection at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
#### ZAP additional information

The page results were successfully manipulated using the boolean conditions `[ZAP AND 1=1 -- ]` and `[ZAP AND 1=2 -- ]`
The parameter value being modified was NOT stripped from the HTML output for the purposes of the comparison
Data was returned for the original parameter.
The vulnerability was detected by successfully restricting the data originally returned, by manipulating the parameter
#### ZAPs solution

Do not trust client side input, even if there is client side validation in place.
In general, type check all data on the server side.

If the application uses JDBC, use PreparedStatement or CallableStatement, with parameters passed by '?'

If the application uses ASP, use ADO Command Objects with strong type checking and parameterized queries.

If database Stored Procedures can be used, use them.

Do *not* concatenate strings into queries in the stored procedure, or use 'exec', 'exec immediate', or equivalent functionality!

Do not create dynamic SQL queries using simple string concatenation.

Escape all data received from the client.

Apply an 'allow list' of allowed characters, or a 'deny list' of disallowed characters in user input.

Apply the principle of least privilege by using the least privileged database user possible.

In particular, avoid using the 'sa' or 'db-owner' database users. This does not eliminate SQL injection, but minimizes its impact.

Grant the minimum database access that is necessary for the application.
#### Flask Solution

1. **Parameterized Queries:** Use parameterized queries or prepared statements provided by the database libraries (e.g., SQLAlchemy) in Flask. These help separate SQL logic from user inputs, preventing direct concatenation of user data into SQL queries.

Example using SQLAlchemy ORM:

```python
from flask_sqlalchemy import SQLAlchemy  

# Assuming `db` is your SQLAlchemy
object result = db.session.execute("SELECT * FROM users WHERE username = :username", {"username": user_input})
```

2. **ORM (Object-Relational Mapping):** Prefer using ORM libraries like SQLAlchemy, which offer ORM features and automatically handle parameterization and sanitation of SQL queries.

Example using SQLAlchemy ORM:

```python
from flask_sqlalchemy import SQLAlchemy  

# Assuming `db` is your SQLAlchemy object and User is the model
users = User.query.filter_by(username=user_input).all()
```


3. **Input Validation and Sanitization:** Validate and sanitize user inputs to ensure they match expected data types and formats. Use validation libraries or custom validation logic to prevent malicious inputs.

4. **Avoid Dynamic SQL:** Minimize dynamic construction of SQL queries based on user inputs. Prefer static SQL queries or parameterized queries to mitigate injection risks.

5. **Least Privilege Principle:** Ensure the database user used by your Flask application has limited privileges, only granting necessary access to perform required operations.
### Path traversal

Path Traversal at [http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)
#### ZAPs solution

Assume all input is malicious. Use an "accept known good" input validation strategy, i.e., use an allow list of acceptable inputs that strictly conform to specifications. Reject any input that does not strictly conform to specifications, or transform it into something that does. Do not rely exclusively on looking for malicious or malformed inputs (i.e., do not rely on a deny list). However, deny lists can be useful for detecting potential attacks or determining which inputs are so malformed that they should be rejected outright.

When performing input validation, consider all potentially relevant properties, including length, type of input, the full range of acceptable values, missing or extra inputs, syntax, consistency across related fields, and conformance to business rules. As an example of business rule logic, "boat" may be syntactically valid because it only contains alphanumeric characters, but it is not valid if you are expecting colors such as "red" or "blue."

For filenames, use stringent allow lists that limit the character set to be used. If feasible, only allow a single "." character in the filename to avoid weaknesses, and exclude directory separators such as "/". Use an allow list of allowable file extensions.

Warning: if you attempt to cleanse your data, then do so that the end result is not in the form that can be dangerous. A sanitizing mechanism can remove characters such as '.' and ';' which may be required for some exploits. An attacker can try to fool the sanitizing mechanism into "cleaning" data into a dangerous form. Suppose the attacker injects a '.' inside a filename (e.g. "sensi.tiveFile") and the sanitizing mechanism removes the character resulting in the valid filename, "sensitiveFile". If the input data are now assumed to be safe, then the file may be compromised. 

Inputs should be decoded and canonicalized to the application's current internal representation before being validated. Make sure that your application does not decode the same input twice. Such errors could be used to bypass allow list schemes by introducing dangerous inputs after they have been checked.

Use a built-in path canonicalization function (such as realpath() in C) that produces the canonical version of the pathname, which effectively removes ".." sequences and symbolic links.

Run your code using the lowest privileges that are required to accomplish the necessary tasks. If possible, create isolated accounts with limited privileges that are only used for a single task. That way, a successful attack will not immediately give the attacker access to the rest of the software or its environment. For example, database applications rarely need to run as the database administrator, especially in day-to-day operations.

When the set of acceptable objects, such as filenames or URLs, is limited or known, create a mapping from a set of fixed input values (such as numeric IDs) to the actual filenames or URLs, and reject all other inputs.

Run your code in a "jail" or similar sandbox environment that enforces strict boundaries between the process and the operating system. This may effectively restrict which files can be accessed in a particular directory or which commands can be executed by your software.

OS-level examples include the Unix chroot jail, AppArmor, and SELinux. In general, managed code may provide some protection. For example, java.io.FilePermission in the Java SecurityManager allows you to specify restrictions on file operations.

This may not be a feasible solution, and it only limits the impact to the operating system; the rest of your application may still be subject to compromise.

#### Solution for flask

1. **Input Validation and Sanitization:** Ensure that user input, especially file paths or directory names, undergoes rigorous validation. Sanitize inputs by verifying that they contain only allowed characters, formats, or patterns.

2. **Use Flask's `safe_join` Function:** Flask provides a `safe_join` function within its `werkzeug` utility library. This function safely joins paths, preventing directory traversal attacks. Use it when constructing file paths.

```python
from werkzeug.utils import safe_join  

path = safe_join('/path/to/allowed/directory', user_provided_input)
```

3. **Serve Files Safely:** If your application serves files, avoid using user-provided input directly as a path. Instead, validate the path and retrieve the file using secure methods.

4. **Restrict File Access:** Configure your web server or application to restrict access to sensitive directories. For instance, utilize proper permissions and access controls to limit file system access.

5. **Security Libraries:** Consider using security-focused libraries or middleware designed for Flask security, such as Flask-Security or Flask-Principal. These might offer additional protections against path traversal and other vulnerabilities.

