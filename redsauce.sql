SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `redsauce`
--

-- --------------------------------------------------------

--
-- Table structure for table `imdb`
--

CREATE TABLE IF NOT EXISTS `imdb` (
  `id` int(11) NOT NULL,
  `primary_title` varchar(255) NOT NULL,
  `year` int(11) NOT NULL,
  `runtime_minutes` int(11) NOT NULL,
  `genres` varchar(255) NOT NULL,
  `avg_rating` int(11) NOT NULL,
  `num_votes` int(11) NOT NULL,
  `processed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `num_votes` (`num_votes`,`processed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `imdb_meta`
--

CREATE TABLE IF NOT EXISTS `imdb_meta` (
  `id` int(11) NOT NULL,
  `omdb_json` mediumtext,
  `fetched_at` timestamp NULL DEFAULT NULL,
  `tomato_id` int(11) DEFAULT NULL,
  `tomato_rating` int(11) DEFAULT NULL,
  `tomato_reviews` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

