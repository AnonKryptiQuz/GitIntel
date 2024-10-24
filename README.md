# GitIntel: GitHub OSINT Tool

**GitIntel** is a powerful GitHub OSINT tool designed to unearth hidden insights from GitHub repositories and user profiles. This tool allows users to extract valuable information, such as emails, from GitHub activities and repositories, making it an essential asset for ethical hacking and security testing.

## **Features**

- **User Information Retrieval**: Collects comprehensive data about GitHub users, including bio, company, location, followers, and more.
- **Email Extraction**: Gathers emails from commits and public events, with options to include hidden emails.
- **Repository Analysis**: Retrieves and analyzes repositories owned by the user.
- **Event Tracking**: Monitors public events to discover additional information.
- **Customizable Options**: Offers advanced configuration for email collection based on user activity.

## **Prerequisites**

- **Python 3.7+**
- **requests** (For making HTTP requests)
- **prompt_toolkit** (For user input and path completion)
- **colorama** (For colored terminal output)

## **Installation**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YourUsername/GitIntel.git
   cd GitIntel
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

   **Ensure `requirements.txt` contains:**

   ```text
   requests==2.28.1
   prompt_toolkit==3.0.36
   colorama==0.4.6
   ```

## **Configuration**

To configure the API endpoint and potentially increase the rate limit, locate the following line in the script and replace it with your specific API path or key:

```python
self.base_url = "https://api.github.com/"
```

If you prefer, you can also continue using this default API.

## **Usage**

1. **Run the tool:**

   ```bash
   python GitIntel.py
   ```

2. **Enter the GitHub username when prompted.**

3. **Choose advanced options to configure email extraction preferences.**

4. **View the results displayed in the terminal and save them to a file if desired.**

## **Disclaimer**

- **Educational Purposes Only**: GitIntel is intended for educational and research use. The tool should not be used for illegal or malicious activities. It is the user’s responsibility to ensure compliance with local laws and regulations.

## **Author**

**Created by:** [AnonKryptiQuz](https://AnonKryptiQuz.github.io/)
