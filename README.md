This program is a desktop application created with the Qt Framework in Python. It provides a user interface for tracking the availability status of specific products on the Nike online store.

The application maintains a list of SKUs (Stock Keeping Units), which the user can modify by adding new SKUs. Each SKU represents a particular product in Nike's online catalogue. The availability status of each product is tracked and updated regularly.

When launched, the application reads a list of SKUs from a text file and initializes a table displaying each SKU and its corresponding status. The status can be one of three possible states: Available, Unavailable, or Pending.

The program uses asynchronous network requests to gather data on each product's availability. Specifically, it uses aiohttp for the network requests and BeautifulSoup for parsing the HTML response. This operation is carried out in a separate thread to avoid blocking the user interface.

When a product's status changes from either Unavailable or Pending to Available, the program sends a desktop notification to alert the user.

The user interface includes buttons for submitting new SKUs to the list and quitting the application. The SKU list is saved to the same text file upon application exit, preserving the state for the next launch.
