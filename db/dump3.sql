-- MariaDB dump 10.19-11.2.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: chat
-- ------------------------------------------------------
-- Server version	11.2.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `conversation`
--

DROP TABLE IF EXISTS `conversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conversation` (
  `conversation_id` int(11) NOT NULL,
  `conversation_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversation`
--

LOCK TABLES `conversation` WRITE;
/*!40000 ALTER TABLE `conversation` DISABLE KEYS */;
INSERT INTO `conversation` VALUES
(1,'memy');
/*!40000 ALTER TABLE `conversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversation_member`
--

DROP TABLE IF EXISTS `conversation_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conversation_member` (
  `user_email` varchar(100) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `joined_datetime` datetime DEFAULT NULL,
  `left_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`user_email`,`conversation_id`),
  KEY `conversation_id` (`conversation_id`),
  CONSTRAINT `conversation_member_ibfk_1` FOREIGN KEY (`user_email`) REFERENCES `user` (`user_email`),
  CONSTRAINT `conversation_member_ibfk_2` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversation_member`
--

LOCK TABLES `conversation_member` WRITE;
/*!40000 ALTER TABLE `conversation_member` DISABLE KEYS */;
/*!40000 ALTER TABLE `conversation_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message` (
  `message_id` int(11) NOT NULL,
  `message_text` varchar(1000) DEFAULT NULL,
  `datetime_of_sending` datetime DEFAULT NULL,
  `conversation_id` int(11) DEFAULT NULL,
  `sender_email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`message_id`),
  KEY `conversation_id` (`conversation_id`),
  KEY `sender_email` (`sender_email`),
  CONSTRAINT `message_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`conversation_id`) ON DELETE SET NULL,
  CONSTRAINT `message_ibfk_2` FOREIGN KEY (`sender_email`) REFERENCES `user` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
INSERT INTO `message` VALUES
(1,'hej co tam','2023-11-07 21:26:29',1,NULL);
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_email` varchar(100) NOT NULL,
  `user_name` varchar(100) DEFAULT NULL,
  `user_password` varchar(100) DEFAULT NULL,
  `date_of_join` datetime DEFAULT NULL,
  `user_pk` varchar(500) DEFAULT NULL,
  `salt` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES
('a','a','a','2023-12-05 21:51:59','1',NULL),
('boru@boru.boru','boru','boru','2023-12-12 13:26:07','1',NULL),
('c','c','c','2023-12-06 00:45:24','1',NULL),
('h','h','h','2023-12-05 21:45:01','1',NULL),
('k','k','$2b$12$8A/QxDIv04J2MbwbRi.OZ.vQzrdEiQNvjqXklO.IZl2sYnd4osUNK','2024-01-16 17:41:53','-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzlWhlwG6JbdT+xl8IzAw\ndXUVI/VJSaf7BrwiyifkKAljdMV+ReUOq4kVTvr8+q341GqqzXgszrNAtmzI66gr\ne/kQbaqffIKyBT/9YXqkzsskyfMfFK82G241CRJYoLdkdGY5zkU88kmiikmM5Opr\nGxxzTqTY2VdOc0FwLCwm4dLEKe+x72rprKYwsPqF2PTo8FQ/64yEXD0aLo5nRqoz\nf3r6oMfrNVquF/yTQwk0mWWyThFdzzAuW3s3OiRwgnODYW4EXHHnJ2CtuopyeR76\nXCNN3NnlIzW2vRwREluxtDBkfC7UQcRj/m5keya1ugWI1cA9KqB1n6Cf5KfrgWlH\nFQIDAQAB\n-----END PUBLIC KEY-----\n','$2b$12$8A/QxDIv04J2MbwbRi.OZ.'),
('s','s','$2b$12$TorLSwKMJjuf1EotJfT81uKD3KbyDXM4nFIRZ9zgMOyI6wSdkinWy','2024-01-16 17:17:04','-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlo9zzqRjVDOpwu68nEFC\nE2YO2Bq7KlY1135Ur42twioZpjFsQ4XyyUm9/719+N90n/FDnkjMDNOXA9P66JGA\n6uuZnizX1Ce5LNXM8QD8BR10f6AW01v8f/YhPR17VGR61vECM6GOCWKRukzMh1ST\nfxAWEQ0Vv+hobNtUEOFeBsNtp/JT5FVPxz1zg6aU5sUiiEiTM+0UjXCkatopUe0D\nPAQOfpuOxJSvpEW+uidMl6fjtXS0DyZqL6AD3fJKqfaKgoX1rtF1hgtrQgeYPQYr\n+KXr6DtRJxfw3oKWQib2TlP56z2eUBe676LiA+jSc+ZHQBpcsOitMoL5jXrnjk4y\n9wIDAQAB\n-----END PUBLIC KEY-----\n','$2b$12$TorLSwKMJjuf1EotJfT81u'),
('u','u','$2b$12$TpdKYq80nc6vRdYUnD/OPeoQp38fn3vivyfBS9CkrmBHLbw./InNO','2024-01-16 17:26:41','-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxvzRTa8oF2S5yYoBbiJu\nIFK14fXC/3TNAneg8CUPueQTBBXa3EsT+I4W5dm1swfuHUbl4AjdzY4Pz8Wfg8CP\nlxubrpyW5BDpnGXjIDBsrJlflNmIWCRen8FXjIbEXFVPcWiEEjtZ+MYhVI9Yq4na\nE9lzU8a1qWhqxI8MlAAllY86AIO6ZDkNR9rMaMoTSkWZFt8uzvjxEGCk6A16l0lw\nCN9Vs8NW1Cya3fstU1/+Q+jHmZtVXcagBEjq+R8AbC3MC+bERb5T/NbKFUqocS2q\n6J6/i7xVAVvE2CwphkPjP8TTxIXmTlg4d05p57r3JhqpTZ32fO9DPhBgmoMBu69v\n3QIDAQAB\n-----END PUBLIC KEY-----\n','$2b$12$TpdKYq80nc6vRdYUnD/OPe'),
('Wicko','Wicko','Wicko','2023-12-11 21:49:35','1',NULL),
('y','y','$2b$12$/.Ck1/RTtq4YtZmjt26YXOYLmLJ8pCbbLBPu25qmqkNfQo9gI28uW','2024-01-16 17:17:34','-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxpHrDOmJmfKpZf5ZmXn\nN47uxW5pTQdUMWY7W+3JAVz0RPlHg4TtJVG9wiU0eH3/1IfTMam0Na7vA4knlFKc\nHHn/wyYArf6h6g9PqBnbQJoK5n4WW5loAjcbVy0x7zTtFld/Zu55nnme52ubRBY6\n9tpwMvfzh20tjrcq8wC2DJTF5ex3x/QCYYzcksJjEhZgbrgnoqo3rpVFBcn4DOR0\ndHEdMVCT86HeKiGlc/MFdOIR7fqkU+zW/aG/2E5L4hxOj3UwxqnihJfkeVtePk2K\nZNel5ACGX5MbM/tOxuqlt7E6z1gK8FksehsMyKouDep4tct6dkl29WxkdwEbbYbc\nuQIDAQAB\n-----END PUBLIC KEY-----\n','$2b$12$/.Ck1/RTtq4YtZmjt26YXO');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-16 19:22:51
