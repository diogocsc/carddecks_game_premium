# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class PremiumDecksController(http.Controller):
    def _require_premium(self):
        user = request.env.user
        if user._is_public():
            raise AccessError("Authentication required")
        subscription = request.env["user.subscription"].sudo().get_user_subscription(user.id)
        if not subscription or subscription.plan_type != "premium":
            raise AccessError("Premium subscription required")
        return subscription

    def _get_owned_deck(self, deck_id):
        deck = request.env["carddecks.deck"].sudo().browse(int(deck_id))
        if not deck.exists():
            return None
        if deck.creator_user_id.id != request.env.user.id:
            raise AccessError("Not your deck")
        return deck

    @http.route("/my/decks", type="http", auth="user", website=True)
    def my_decks(self, **kwargs):
        self._require_premium()
        user = request.env.user
        decks = request.env["carddecks.deck"].sudo().search(
            [("creator_user_id", "=", user.id)],
            order="creation_date desc, id desc",
        )
        return request.render(
            "carddecks_game_premium.my_decks_page",
            {"decks": decks, "user": user},
        )

    @http.route("/my/deck/new", type="http", auth="user", website=True, methods=["GET", "POST"])
    def deck_new(self, **post):
        self._require_premium()
        user = request.env.user

        if request.httprequest.method == "GET":
            categories = request.env["carddecks.category"].sudo().search([])
            return request.render(
                "carddecks_game_premium.deck_edit_page",
                {
                    "mode": "create",
                    "deck": None,
                    "categories": categories,
                    "user": user,
                },
            )

        values = {
            "name": (post.get("name") or "").strip(),
            "description": (post.get("description") or "").strip(),
            "category": int(post.get("category")) if post.get("category") else False,
            "creator_user_id": user.id,
            "is_user_created": True,
            "is_public": bool(post.get("is_public")),
            "approval_status": "draft" if post.get("is_public") else "approved",
            "listing_status": post.get("listing_status") or "private",
            "sale_price": float(post.get("sale_price") or 0.0),
        }

        deck = request.env["carddecks.deck"].sudo().create(values)

        # Optional: create cards from textarea (one per line)
        cards_raw = (post.get("cards_text") or "").strip()
        if cards_raw:
            Card = request.env["carddecks.card"].sudo()
            for line in cards_raw.splitlines():
                text = line.strip()
                if text:
                    Card.create({"cardText": text, "deck": deck.id})

        return request.redirect("/my/decks")

    @http.route("/my/deck/<int:deck_id>/edit", type="http", auth="user", website=True, methods=["GET", "POST"])
    def deck_edit(self, deck_id, **post):
        self._require_premium()
        deck = self._get_owned_deck(deck_id)
        if not deck:
            return request.not_found()

        if request.httprequest.method == "GET":
            categories = request.env["carddecks.category"].sudo().search([])
            return request.render(
                "carddecks_game_premium.deck_edit_page",
                {
                    "mode": "edit",
                    "deck": deck,
                    "categories": categories,
                    "user": request.env.user,
                },
            )

        write_vals = {
            "name": (post.get("name") or "").strip(),
            "description": (post.get("description") or "").strip(),
            "category": int(post.get("category")) if post.get("category") else False,
            "is_public": bool(post.get("is_public")),
            "listing_status": post.get("listing_status") or deck.listing_status,
            "sale_price": float(post.get("sale_price") or 0.0),
        }
        # If user requests public visibility, require approval cycle
        if write_vals["is_public"]:
            write_vals["approval_status"] = "draft"
        deck.sudo().write(write_vals)

        # Add new cards (optional)
        cards_raw = (post.get("cards_text") or "").strip()
        if cards_raw:
            Card = request.env["carddecks.card"].sudo()
            for line in cards_raw.splitlines():
                text = line.strip()
                if text:
                    Card.create({"cardText": text, "deck": deck.id})

        return request.redirect("/my/decks")

    @http.route("/my/deck/<int:deck_id>/delete", type="http", auth="user", website=True, methods=["POST"])
    def deck_delete(self, deck_id, **post):
        self._require_premium()
        deck = self._get_owned_deck(deck_id)
        if not deck:
            return request.not_found()
        # Delete cards first to avoid constraint issues on some setups
        deck.cards.sudo().unlink()
        deck.sudo().unlink()
        return request.redirect("/my/decks")

