from flask.ext.migrate import Migrate, MigrateCommand
from flask_script import Manager

from utils.app import create_app, db

app = create_app()

manage = Manager(app=app)
migrate = Migrate(app, db)  # 将app与db关联
manage.add_command('db', MigrateCommand)
if __name__ == '__main__':
    manage.run()
