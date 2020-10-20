DROP DATABASE IF EXISTS data_processing;
CREATE DATABASE data_processing;
USE data_processing;

CREATE TABLE `papers` (
    `id` varchar(255) NOT NULL,
    `title` varchar(255) COLLATE utf8_bin NOT NULL,
    `abs` varchar(4095) COLLATE utf8_bin NOT NULL,
    `publication` varchar(255) COLLATE utf8_bin NOT NULL,
    `publicationDate` varchar(255) COLLATE utf8_bin NOT NULL,
    `link` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `domains` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `affiliation` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    `description` varchar(4095) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `publication` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    `publication_date` varchar(255) COLLATE utf8_bin NOT NULL,
    `impact` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `researcher` (
    `id` varchar(255) NOT NULL,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


CREATE TABLE `paper_researcher` (
    `id` varchar(255) NOT NULL,
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    `order` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_reference` (
    `id` varchar(255) NOT NULL,
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_domain` (
    `id` varchar(255) NOT NULL,
    `pid` varchar(255) COLLATE utf8_bin NOT NULL,
    `did` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `paper_publication` (
    `id` varchar(255) NOT NULL,
    `paper_id` varchar(255) COLLATE utf8_bin NOT NULL,
    `publication_id` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `researcher_domain` (
    `id` varchar(255) NOT NULL,
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    `did` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `researcher_affiliation` (
    `id` varchar(255) NOT NULL,
    `rid` varchar(255) COLLATE utf8_bin NOT NULL,
    `aid` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;