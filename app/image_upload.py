from . import app, db  # , s3
from .models import Photo
import os
from uuid import uuid4
from PIL import Image

SUCCESS = "SUCCESS"
INVALID_FILENAME = "INVALID_FILENAME"
INVALID_FORMAT = "INVALID_FORMAT"
INVALID_SIZE = "INVALID_SIZE"


def save_photo(picture_data, owner_model):
    uploaded_filename = picture_data.filename

    if uploaded_filename == "" or uploaded_filename is None:
        return INVALID_FILENAME
    else:
        filename = uploaded_filename.split(".")
        extension = filename[-1].lower()

        if extension not in app.config["ALLOWED_IMG_FORMATS"]:
            return INVALID_FORMAT
        else:
            while True:
                filename = str(uuid4())
                if Photo.query.filter_by(filename=filename).first() is None:
                    break

            new_filename = filename + "." + extension

            # --Beautiful-- trick getting size of image
            picture_data.seek(0, os.SEEK_END)
            size = picture_data.tell()
            if size > app.config["ALLOWED_IMG_SIZE"]:
                return INVALID_SIZE
            picture_data.seek(0)

            full_filename = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
            picture_data.save(full_filename)
            # s3.upload_file(full_filename, new_filename)

            if owner_model.image is not None:
                """
                try:
                    s3.delete_objects(Delete=
                    {
                        'Objects':
                        [
                            {
                                'Key': owner_model.image.filename
                            }
                        ]
                    })
                except:
                    pass
                """

                old_picture = os.path.join(
                    app.config["UPLOAD_FOLDER"], owner_model.image.filename
                )
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
