# -*- coding: utf-8 -*-
{
    "name": "Card Decks Game Premium",
    "version": "16.0.0.0.1",
    "author": "Diogo Cordeiro",
    "summary": "Premium users manage their own card decks",
    "category": "Services/Card Decks",
    "depends": [
        "website",
        "portal",
        "carddecks",
        "carddecks_game",
        "subscription_plans",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/rules.xml",
        "views/website_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "carddecks_game_premium/static/src/css/premium_decks.css",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

