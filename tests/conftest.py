import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    app.db.engine.execute('DROP TABLE IF EXISTS `customer`;')

    app.db.engine.execute('''CREATE TABLE `customer` (
  `cust_id` int NOT NULL AUTO_INCREMENT,
  `cust_name` varchar(225) NOT NULL,
  `cust_phone` int NOT NULL,
  `cust_email` varchar(225) NOT NULL,
  UNIQUE (cust_email),
  PRIMARY KEY (`cust_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;''')

    app.db.engine.execute(
        '''INSERT INTO `customer` VALUES
        (1,'Carmen Yip',98765432,'carmenyip@abc.com'),(2,'Nikki Poo',97654321,'nikkipoo@abc.com'),
        (3,'Jie Mi',96543218,'jiemi@abc.com');''')

    return app.app.test_client()
