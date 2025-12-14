# Capability 6-Pack App

This application generates a "Capability 6-Pack" report (Control Charts, Histograms, Capability Indices) from a CSV file.

## Setup

1.  Ensure you have Python installed.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

To start the application, run the following command in your terminal:

```bash
streamlit run app.py
```

Alternatively, if you prefer running it directly with Python:

```bash
python run.py
```

## Usage

1.  The app will open in your default web browser.
2.  Upload a CSV file containing your measurement data.
3.  Select the column (dimension) you want to analyze.
4.  Enter the Lower Spec Limit (LSL) and Upper Spec Limit (USL).
5.  (Optional) Check "Specify Target?" to enter a target value.
6.  Click "Generate Report".
7.  To print, press `Ctrl + P` (or Cmd + P) and save as PDF. The interface is optimized to hide the sidebar when printing.
