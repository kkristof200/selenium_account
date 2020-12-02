# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
import time
from abc import abstractmethod
from typing import Optional, List, Tuple

# Pip
from selenium_firefox import Firefox

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: SeleniumAccount -------------------------------------------------------- #

class SeleniumAccount:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        cookies_folder_path: Optional[str] = None,
        extensions_folder_path: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        cookies_id: Optional[str] = None,
        firefox_binary_path: Optional[str] = None,
        private: bool = False,
        screen_size: Optional[Tuple[int, int]] = None,
        full_screen: bool = True,
        headless: bool = False,
        language: str = 'en-us',
        user_agent: Optional[str] = None,
        disable_images: bool = False,
        default_find_func_timeout: int = 2.5,
        prompt_login: bool = True
    ):
        self.browser = Firefox(
            cookies_folder_path=cookies_folder_path,
            extensions_folder_path=extensions_folder_path,
            host=host,
            port=port,
            cookies_id=cookies_id,
            firefox_binary_path=firefox_binary_path,
            private=private,
            screen_size=screen_size,
            full_screen=full_screen,
            headless=headless,
            language=language,
            user_agent=user_agent,
            disable_images=disable_images,
            default_find_func_timeout=default_find_func_timeout
        )

        self.browser.get(self.home_url)

        try:
            if not self.browser.login_via_cookies(self.home_url, None) and prompt_login:
                input('Log in and press Enter/Return: ')

                if self.is_logged_in:
                    self.save_cookies()

            if self.browser.has_cookies_for_current_website():
                time.sleep(0.5)
                self.browser.get(self.home_url)
                time.sleep(0.5)
                self.save_cookies()
        except Exception as e:
            print(e)
            self.quit()

        if not self.is_logged_in:
            print('Could not log in')


    # ----------------------------------------------------- Abstract properties ------------------------------------------------------ #

    @abstractmethod
    def _home_url(self) -> str:
        pass

    @abstractmethod
    def _is_logged_in(self) -> bool:
        pass


    # ------------------------------------------------------ Public properties ------------------------------------------------------- #

    @property
    def home_url(self) -> str:
        return self._home_url()

    @property
    def is_logged_in(self) -> bool:
        return self._is_logged_in()


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def save_cookies(self) -> None:
        self.browser.save_cookies()

    def quit(self) -> None:
        try:
            self.browser.driver.quit()
        except:
            pass


    # ------------------------------------------------------ Private properties ------------------------------------------------------ #



    # ------------------------------------------------------- Private methods -------------------------------------------------------- #


# ---------------------------------------------------------------------------------------------------------------------------------------- #