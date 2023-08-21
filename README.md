# Social Medi Api
The API allows users to create profiles, follow other users, create and retrieve posts, manage likes and comments, and perform basic social media actions

1. Clone the repository:

   ```shell
   git clone https://github.com/KirillMelanich/social-media-api.git
   
2. Navigate to the project directory and activate virtual environment:
   ```shell
   cd social_media_api
   python3 - venv venv
   venv/Scripts/activate(on Windows)
   source venv/bin/activate(on Mac)
   
3. Install dependencies:
   ```shell
    pip install -r requirements.txt
   
4. Perform database migrations:
    ```shell
    python manage.py migrate

5. Add these apps to `INSTALLED_APPS` and install them corresponding to the `rest_framework` version.

      ```python
        INSTALLED APPS = [
      ...,
      "rest_framework",
   ]
   ```

## Usage

1. Run the development server:
     ```shell
    python manage.py runserver
2. Open your web browser and visit:
    ```shell 
    http://localhost:8000/

# Features


### JWT authenticated
### Admin panel /admin/
### Documentation is located at api/doc/swagger/
### User profile creation and updating with profile picture, bio, and other details
### User profile retrieval and searching for users by username or other criteria
### Follow/unfollow functionality with the ability to view lists of followed and following users
### Post creation with text content and optional media attachment
### Users сan like/unlike posts, view the list of posts they have liked
### Users can add comments to posts and view comments on posts.
