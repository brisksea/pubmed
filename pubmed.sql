-- phpMyAdmin SQL Dump
-- version 4.1.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: 2017-01-02 23:32:48
-- 服务器版本： 5.6.17
-- PHP Version: 5.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `pubmed`
--

-- --------------------------------------------------------

--
-- 表的结构 `geneintact`
--

CREATE TABLE IF NOT EXISTS `geneintact` (
  `gene1` varchar(30) NOT NULL,
  `gene2` varchar(30) NOT NULL,
  `docId` varchar(20) NOT NULL,
  `sentId` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `mention`
--

CREATE TABLE IF NOT EXISTS `mention` (
  `docId` varchar(10) NOT NULL,
  `sentId` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `start` smallint(6) DEFAULT NULL,
  `end` smallint(6) DEFAULT NULL,
  `dbId` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `sentence`
--

CREATE TABLE IF NOT EXISTS `sentence` (
  `docId` varchar(20) NOT NULL,
  `sentId` int(11) NOT NULL,
  `content` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`docId`,`sentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
