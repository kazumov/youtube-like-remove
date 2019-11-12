#!/usr/bin/env python3

from __future__ import annotations

# -*- coding: utf-8 -*-

__description__ = "Remove all youtube likes"
__copyright__ = "2019 Ruben R. Kazumov"

import os, sys
from typing import Any
import asyncio
from pyppeteer import launch, page, browser
from pyppeteer.errors import ElementHandleError, TimeoutError
from console import Console


class User:
    """The user credentials.
    
    Attributes:
    - login (str): User Login
    - password (str): User Password"""

    def __init__(self, login: String = "", password: String = ""):
        super().__init__()
        self.login = login
        self.password = password


class URL:
    """URL to YouTube application.
    
    Attributes:
    - home (str): YouTube Application URL
    - accounts (str): Goole Accounts Application URL"""

    home = r"https://youtube.com"
    accounts = r"https://accounts.google.com/ServiceLogin/signinchooser?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3D%252F&hl=en&ec=65620&flowName=GlifWebSignIn&flowEntry=ServiceLogin"


class GoogleAccountsSelectors:
    """Selectors for the Google Accounts application.
    
    Attributes:
    - login (str): E-mail field. Global.
    - password (str): Password field. Global."""

    login = r"input[type='email']"
    passwrod = r"input[type='password']"


class YouTubeSelectors:
    """Selectors for the YouTube application.

    Attributes:
    - page (str): Global page selector. Global.
    - pageContent (str): Page content selector. Under `page` selector.
    - guideButton (str): Expand/slide-in navbar button. Under `pageContent` selector.
    - drawer (str): Navbar container. Under `page` selector.
    - likedVideos (str): `Liked videos` navigator button. Under `drawer` selector.
    - browser (str): Two-pane video browser. Under `pageContent`.
    - listItems (str): List of liked videos. Under `browser`.
    - itemInList (str): Single liked video. Under `listItems`.
    - menuButton (str): [RELATIVE] Menu button of single video. Under `itemInList`.
    - caption (str): [RELATIVE] Video caprion. Under `itemInList`.
    - popUp (str): Pop-up menu. Under `drawer`.
    - menuElement (str): Pop-up menu element. Under `popUp`."""

    page = r"ytd-app"
    pageContent = r"ytd-app > #content.ytd-app"
    guideButton = r"#guide-button"
    drawer = r"ytd-app > app-drawer#guide"
    likedVideos = r"a#endpoint[title='Liked videos']"
    browser = r"ytd-browse"
    listItems = r"ytd-playlist-video-list-renderer"
    itemInList = r"ytd-playlist-video-list-renderer, ytd-playlist-video-renderer"
    menuButton = r"button#button[aria-label='Action menu']"
    caption = r"#video-title"
    popUp = r"ytd-popup-container"
    menuElement = r"ytd-popup-container ytd-menu-service-item-renderer[role='menuitem']"
    menuElementCaption = r"yt-formatted-string"


if __name__ == "__main__":

    async def doLogin(
        user: User, browser: pyppeteer.browser, page: pyppeteer.page
    ) -> None:
        """Login to the account
        
        Parameters:
        - user (User): User credentials.
        - browser (pyppeteer.browser): Reference to the active browser.
        - page (pyppeteer.page): Reference to the active page."""

        Console.info(
            f"Attempt to login into Google Accounts for the user `{user.login}`..."
        )
        await page.goto(URL.accounts, waitUntil="networkidle0")
        Console.info("- Google Accounts page navigated.")
        await page.waitForSelector(GoogleAccountsSelectors.login)
        Console.info("- E-mail field is visible.")
        await page.keyboard.type(user.login)
        Console.info("- Login entered.")
        await page.keyboard.press("Enter")
        Console.info("- `ENTER` pressed.")
        await page.waitForNavigation(waitUntil="networkidle0")
        await page.waitFor(500)
        Console.info("- Navigation to the password section completed.")
        await page.waitForSelector(GoogleAccountsSelectors.passwrod)
        Console.info("- Password field is visible.")
        await page.focus(GoogleAccountsSelectors.passwrod)
        Console.info("- Password field selected.")
        await page.keyboard.type(user.password)
        Console.info("- Password entered.")
        await page.keyboard.press("Enter")
        Console.info("- `ENTER` pressed.")
        await page.waitForNavigation(waitUntil="networkidle0")
        Console.info("- Redirected after the login.")
        Console.info("Logged in.")

    async def browseYouTubeLikes(
        browser: pyppeteer.browser, page: pyppeteer.page
    ) -> None:
        """Open YouTube, navigate to user's liked videos library
        
        Parameters:
        - browser (pyppeteer.browser): Reference to the active browser.
        - page (pyppeteer.page): Reference to the active page."""

        Console.info(f"Attempt to open the list of liked videos...")
        await page.goto(URL.home, waitUntil="networkidle0")  # reload
        Console.info("- YouTube page navigated.")
        youTube = await page.waitForSelector(YouTubeSelectors.page)
        Console.info("- Page loaded.")
        pageContent = await page.waitForSelector(YouTubeSelectors.pageContent)
        Console.info("- Content loaded.")
        guideButton = await page.waitForSelector(YouTubeSelectors.guideButton)
        Console.info("- Menu button is visible.")
        await guideButton.click()
        Console.info("- Menu button clicked.")
        await page.waitForSelector(YouTubeSelectors.drawer)
        Console.info("- Navigator panel is visible.")
        likedVideos = await page.waitForSelector(YouTubeSelectors.likedVideos)
        Console.info("- Navigator button to likes is visible.")
        href = await page.Jeval(
            YouTubeSelectors.likedVideos, "e => e.getAttribute('href')"
        )
        Console.info(f"- The URL to the list of liked videos: {href}")
        await page.goto(URL.home + href, waitUntil="networkidle0")
        Console.info("- Playlist loaded.")
        browser = await page.waitForSelector(YouTubeSelectors.browser)
        Console.info("- Videos browser is visible.")
        listItems = await page.waitForSelector(YouTubeSelectors.listItems)
        Console.info("- List of liked videos is visible.")
        Console.info(f"Navigated to the list of liked videos.")

    async def removeLast(browser: pyppeteer.browser, page: pyppeteer.page) -> None:
        """Removes the top item of list

        Parameters:
        - browser (pyppeteer.browser): Reference to the active browser.
        - page (pyppeteer.page): Reference to the active page."""

        Console.info(f"Attempt to delete the last liked video from the list...")
        # await page.waitForSelector(YouTubeSelectors.listItems)
        Console.info(f"- Counting the list elements.")
        listItems = await page.JJ(YouTubeSelectors.itemInList)
        if listItems == []:
            Console.info("No items found.")
            return

        Console.info(f"- The list contains {len(listItems)} videos.")

        item = listItems[0]

        caption = await item.Jeval(
            YouTubeSelectors.caption, r"caption => caption.getAttribute('title')"
        )

        Console.info(f"- The last liked video is `{caption}`.")
        Console.info("- Activating of the pop-up menu...")
        await item.Jeval(YouTubeSelectors.menuButton, "btn => btn.click()")
        Console.info("- Menu button clicked.")
        await page.waitForSelector(YouTubeSelectors.popUp)
        Console.info("- Pop-up menu is visible.")
        menuItems = await page.JJ(YouTubeSelectors.menuElement)
        Console.info(f"- Found {len(menuItems)} menu items.")
        for itm in menuItems:
            Console.info("- Reading the menu items captions.")
            try:
                caption = await itm.Jeval(
                    YouTubeSelectors.menuElementCaption, "el => el.innerText"
                )
            except:
                Console.info("- Wrong item. Jump to the next one.")
                continue  # next element in for-loop

            Console.info(f"- Menu item `{caption}`...")
            if caption == "Remove from Liked videos":
                Console.info("- Ready to simulate click on remove menu item.")
                await itm.Jeval(YouTubeSelectors.menuElementCaption, "el => el.click()")
                Console.info("- `Remove...` menu click simulated.")
                await page.waitFor(1000)  # time to remove element
                Console.info("- 1s pause finished.")
                Console.info("- Item removed.")

    async def main():
        """Removes 3 last liked videos from the User YouTube account."""
        browser = await launch(headless=True)
        page = await browser.newPage()

        # login
        try:
            await doLogin(
                User("LOGIN", "PASSWORD"),
                browser,
                page,
            )
        except Exception as e:
            Console.error("Inpossible to login:")
            print(e)
            await browser.close()
            return

        # likes
        try:
            await browseYouTubeLikes(browser, page)
        except Exception as e:
            Console.error(
                "Problem with the navigation to the YouTube liked videos library:"
            )
            print(e)
            await browser.close()
            return

        # removal
        try:
            await removeLast(browser, page)
        except Exception as e:
            Console.error("Problem with the video removal.")
            print(e)
            await browser.close()
            return

        # finish the process
        await browser.close()
        return

    # clear console window
    os.system("clear")
    asyncio.get_event_loop().run_until_complete(main())

