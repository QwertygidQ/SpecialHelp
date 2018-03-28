from . import app, db
from .models import Photo
import os
from uuid import uuid4

SUCCESS = 0
INVALID_FILENAME = 1
INVALID_FORMAT = 2


def save_photo(picture_data, owner_model):
    uploaded_filename = picture_data.filename

    if uploaded_filename == '' or uploaded_filename is None:
        return INVALID_FILENAME
    else:
        filename = uploaded_filename.split('.')
        extension = filename[-1].lower()

        if extension not in app.config['ALLOWED_IMG_FORMATS']:
            return INVALID_FORMAT
        else:
            while True:
                filename = str(uuid4())
                if Photo.query.filter_by(filename=filename).first() is None:
                    break

            new_filename = filename + '.' + extension
            picture_data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

            if owner_model.image is not None:
                old_picture = os.path.join(app.config['UPLOAD_FOLDER'], owner_model.image.filename)
                try:
                    os.remove(old_picture)
                except FileNotFoundError:
                    pass

                owner_model.image.filename = new_filename
            else:
                owner_model.image = Photo(filename=new_filename)

            db.session.commit()

            owner_model.image.resize()
            owner_model.image.clear_meta()

            return SUCCESS
