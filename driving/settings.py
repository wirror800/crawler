# -*- coding: utf-8 -*-

# Scrapy settings for driving project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'driving'

SPIDER_MODULES = ['driving.spiders']
NEWSPIDER_MODULE = 'driving.spiders'
ITEM_PIPELINES = {
    #'driving.pipelines.ProvincePipeline': 100,
    'driving.pipelines.SchoolPipeline': 200
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'driving (+http://www.yourdomain.com)'
