# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List, Tuple, Callable, Union
from abc import abstractmethod
import time, os

# Pip
from selenium_firefox import Firefox, Proxy, BaseAddonInstallSettings
import tldextract
from kstopit import signal_timeoutable

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: SeleniumAccount -------------------------------------------------------- #

class SeleniumAccount:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,

        # cookies
        cookies_folder_path: Optional[str] = None,
        cookies_id: Optional[str] = None,
        pickle_cookies: bool = False,

        # proxy
        proxy: Optional[Union[Proxy, str]] = None,
        # proxy - legacy (kept for convenience)
        host: Optional[str] = None,
        port: Optional[int] = None,

        # addons
        addons_folder_path: Optional[str] = None,
        addon_settings: Optional[List[BaseAddonInstallSettings]] = None,
        # addons - legacy (kept for convenience)
        extensions_folder_path: Optional[str] = None,

        # other paths
        geckodriver_path: Optional[str] = None,
        firefox_binary_path: Optional[str] = None,
        profile_path: Optional[str] = None,

        # profile settings
        private: bool = False,
        full_screen: bool = True,
        language: str = 'en-us',
        user_agent: Optional[str] = None,
        disable_images: bool = False,

        # option settings
        screen_size: Optional[Tuple[int, int]] = None, # (width, height)
        headless: bool = False,
        mute_audio: bool = False,
        home_page_url: Optional[str] = None,

        # selenium-wire support
        webdriver_class: Optional = None,

        # find function
        default_find_func_timeout: int = 2.5,


        # login
        prompt_user_input_login: bool = True,
        login_prompt_callback: Optional[Callable[[str], None]] = None,
        login_prompt_timeout_seconds: int = 60*5
    ):
        self.browser = Firefox(
            cookies_folder_path=cookies_folder_path,
            cookies_id=cookies_id,
            pickle_cookies=pickle_cookies,

            # proxy
            proxy=proxy,
            # proxy - legacy (kept for convenience)
            host=host,
            port=port,

            # addons
            addons_folder_path=addons_folder_path,
            addon_settings=addon_settings,
            # addons - legacy (kept for convenience)
            extensions_folder_path=extensions_folder_path,

            # other paths
            geckodriver_path=geckodriver_path,
            firefox_binary_path=firefox_binary_path,
            profile_path=profile_path,

            # profile settings
            private=private,
            full_screen=full_screen,
            language=language,
            user_agent=user_agent,
            disable_images=disable_images,

            # option settings
            screen_size=screen_size,
            headless=headless,
            mute_audio=mute_audio,
            home_page_url=home_page_url,

            # selenium-wire support
            webdriver_class=webdriver_class,

            # find function
            default_find_func_timeout=default_find_func_timeout
        )

        self.current_user_id = None

        try:
            self.__internal_id = cookies_folder_path.strip(os.path.sep).split(os.path.sep)[-1]
        except:
            self.__internal_id = cookies_folder_path or self.browser.cookies_folder_path

        self.get(self.home_url)

        try:
            self.did_log_in_at_init = self.login_via_cookies(
                prompt_user_input_login=prompt_user_input_login,
                login_prompt_callback=login_prompt_callback,
                login_prompt_timeout_seconds=login_prompt_timeout_seconds,
                save_cookies=True
            )
        except Exception as e:
            self.print(e)
            self.did_log_in_at_init = False

        if self.did_log_in_at_init:
            self.current_user_id = self._get_current_user_id()


    # ------------------------------------------------------- Abstract methods ------------------------------------------------------- #

    @abstractmethod
    def _home_url(self) -> str:
        pass

    @abstractmethod
    def _get_current_user_id(self) -> Optional[str]:
        pass

    @abstractmethod
    def _profile_url_format(self) -> Optional[str]:
        pass

    @abstractmethod
    def _login_via_cookies_needed_cookie_names(self) -> Union[str, List[str]]:
        pass


    # ------------------------------------------------------ Public properties ------------------------------------------------------- #

    @property
    def current_profile_url(self) -> Optional[str]:
        return self.profile_url(self.current_user_id)

    @property
    def home_url(self) -> str:
        return self._home_url()

    @property
    def is_logged_in(self) -> bool:
        return self.browser.has_all_cookies(self._login_via_cookies_needed_cookie_names())

    @property
    def domain(self) -> str:
        if not hasattr(self, '__domain'):
            self.__domain = tldextract.extract(self.home_url).domain

        return self.__domain

    @property
    def page_name(self) -> str:
        if not hasattr(self, '__page_name'):
            self.__page_name = self.domain.lower().title()

        return self.__page_name

    @property
    def user_agent(self) -> str:
        return self.browser.user_agent

    @property
    def proxy(self) -> Optional[Proxy]:
        return self.browser.proxy


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def profile_url(
        self,
        profile_id: Union[str, int]
    ) -> Optional[str]:
        return self._profile_url_format().format(profile_id) if profile_id else None

    def get_profile(
        self,
        profile_id: Optional[Union[str, int]]
    ) -> bool:
        if not profile_id:
            self.print('Could not get profile, because \'profile_id\' is None')

            return False

        self.get(self.profile_url(profile_id))

        return True

    def login_via_cookies(
        self,
        prompt_user_input_login: bool = True,
        login_prompt_callback: Optional[Callable[[str], None]] = None,
        login_prompt_timeout_seconds: Optional[float] = None,
        save_cookies: bool = True
    ) -> bool:
        login_cookies_result = self.browser.login_via_cookies(self.home_url, self._login_via_cookies_needed_cookie_names())
        login_actual_result = login_cookies_result and self.is_logged_in

        if not login_cookies_result:
            self.print('Could not log in via cookies.')
        elif not login_actual_result:
            self.print('Did find cookies, but could not log in with them.')

        if not login_actual_result:
            if prompt_user_input_login or login_prompt_callback is not None:
                def local_login_prompt_callback(message: str):
                    input(message)

                try:
                    self.__call_login_prompt_callback(
                        login_prompt_callback if login_prompt_callback else local_login_prompt_callback,
                        timeout=login_prompt_timeout_seconds
                    )

                    return self.login_via_cookies(prompt_user_input_login=False, save_cookies=save_cookies)
                except Exception as e:
                    self.print(e)

            self.print('Did not log in.')

            return False

        self.print('Successfully logged in. Saving cookies.')
        time.sleep(0.5)
        self.get(self.home_url)
        time.sleep(0.5)
        self.save_cookies()

        return True

    def print(self, *args, **kwargs) -> None:
        print('{} - {} -'.format(self.page_name, self.__internal_id), *args, **kwargs)

    def save_cookies(self) -> None:
        self.browser.save_cookies()

    def get(
        self,
        url: str,
        force: bool = False
    ) -> bool:
        return self.browser.get(url, force=force)

    def quit(self) -> bool:
        try:
            self.browser.quit()

            return True
        except Exception as e:
            print('Error - SeleniumAcc: quit() - ', e)

            return False


    # --------------------------------------------------------- Destructor ----------------------------------------------------------- #

    def __del__(self):
        try:
            self.quit()
        except Exception as e:
            print('Error - SeleniumAcc: __del__() - ', e)


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @signal_timeoutable(name='login_prompt_callback')
    def __call_login_prompt_callback(
        self,
        login_prompt_callback: Callable[[str], None],
        timeout: float = None
    ) -> None:
        message = '{} - {} - Needs login.'.format(self.page_name, self.__internal_id)

        if timeout:
            message += ' (Timeout: {})'.format(self.__seconds_to_time_str(timeout))

        login_prompt_callback(message)

    @staticmethod
    def __seconds_to_time_str(seconds: float) -> str:
        hours = int(seconds/3600)
        seconds -= hours*3600

        minutes = int(seconds/60)
        seconds -= minutes*60

        millis = seconds - int(seconds)
        seconds = int(seconds)
        time_str = ''

        if hours > 0:
            time_str = str(hours).zfill(2)

        if minutes > 0 or len(time_str) > 0:
            if len(time_str) > 0:
                time_str += ':'

            time_str += str(minutes).zfill(2)

        if seconds > 0 or len(time_str) > 0:
            if len(time_str) > 0:
                time_str += ':'

            time_str += str(seconds).zfill(2)

        if millis > 0:
            time_str += '.'

            time_str += str(int(millis*1000)).rstrip('0')

        return time_str


# ---------------------------------------------------------------------------------------------------------------------------------------- #