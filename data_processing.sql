DROP DATABASE IF EXISTS data_processing;
CREATE DATABASE data_processing;
USE data_processing;

CREATE TABLE `paper` (
    `id` varchar(255) NOT NULL,
    `title` varchar(255) COLLATE utf8_bin NOT NULL,
    `abs` varchar(4095) COLLATE utf8_bin NOT NULL,
    `publication_id` varchar(255) COLLATE utf8_bin NOT NULL,
    `publication_date` varchar(255) COLLATE utf8_bin NOT NULL,
    `link` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `domain` (
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    `url` varchar(255) COLLATE utf8_bin,
    PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `affiliation` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    `description` varchar(4095) COLLATE utf8_bin,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `publication` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    `publication_date` varchar(255) COLLATE utf8_bin NOT NULL,
    `impact` varchar(255) COLLATE utf8_bin DEFAULT '-1',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `researcher` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


CREATE TABLE `paper_researcher` (
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    `order` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`pid`, `rid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_reference` (
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `reference_doi` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`pid`, `reference_doi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_domain` (
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `dname` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`pid`, `dname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_publication` (
    `paper_id` varchar(255) COLLATE utf8_bin NOT NULL,
    `publication_id` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`paper_id`, `publication_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


CREATE TABLE `researcher_affiliation` (
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    `aid` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`rid`, `aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_ieee_reference_document` (
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `ieee_document` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`pid`, `ieee_document`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_reference_citation` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `reference_citation` varchar(4095) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=5212;

CREATE TABLE `paper_reference_title` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `reference_title` varchar(4095) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=314;