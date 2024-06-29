# Culinary Hub

Culinary Hub is a web application designed to help food enthusiasts discover, save, and share their favorite recipes. Whether you're a professional chef or a home cook, Culinary Hub provides a platform to explore culinary creativity and connect with others who share your passion for cooking.

## Features

- **Recipe Discovery:** Browse through a diverse collection of recipes from various cuisines and categories.
- **Recipe Saving:** Save your favorite recipes to access them later from your profile.
- **Recipe Sharing:** Share your own recipes with the community and get feedback.
- **User Profiles:** Customize your profile, manage saved recipes, and view your activity.
- **Search Functionality:** Easily find recipes based on keywords
- **Responsive Design:** Enjoy a seamless experience across devices, from desktops to mobile phones.

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap5
- **Database:** PostgreSQL (Docker image used also)


## Installation

To run Culinary Hub locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/glebka1337/CulinaryHub_v2.git
   cd culinary-hub
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

6. Access the application at `http://localhost:8000` in your web browser.

## Usage

- Create a user account or log in if you already have one.
- Explore recipes by browsing or using the search functionality.
- Save recipes to your profile by clicking the save button.
- Share your own recipes by uploading them via your profile page.
- 
## Contributing

We welcome contributions to Culinary Hub! To contribute:

1. Fork the repository and clone it locally.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test thoroughly.
4. Push to your fork and submit a pull request.

## Contact

Have questions or feedback? Contact me via telegram @mercury489