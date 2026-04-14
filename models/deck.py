# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CardDeckDeck(models.Model):
    _inherit = "carddecks.deck"

    listing_status = fields.Selection(
        [
            ("private", "Private"),
            ("unlisted", "Unlisted"),
            ("listed_free", "Listed (Free)"),
            ("listed_premium", "Listed (Premium)"),
            ("for_sale", "For Sale"),
        ],
        string="Listing Status",
        default="private",
        help="Controls whether your deck is visible to others on the website.",
    )

    sale_price = fields.Float(
        string="Sale Price",
        digits="Product Price",
        help="Displayed when the deck is marked as For Sale. Payment enforcement is not implemented yet.",
    )
    sale_currency_id = fields.Many2one(
        "res.currency",
        string="Sale Currency",
        default=lambda self: self.env.company.currency_id,
    )

    is_available_on_website = fields.Boolean(
        string="Available on Website",
        compute="_compute_is_available_on_website",
        store=True,
    )

    @api.depends("listing_status", "is_public", "approval_status")
    def _compute_is_available_on_website(self):
        for deck in self:
            # Visible only if listed + public + approved
            is_listed = deck.listing_status in ("listed_free", "listed_premium", "for_sale")
            deck.is_available_on_website = bool(is_listed and deck.is_public and deck.approval_status == "approved")

