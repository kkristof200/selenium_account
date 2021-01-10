# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
import time, os
from abc import abstractmethod
from typing import Optional, List, Tuple, Callable

# Pip
from selenium_firefox import Firefox
import tldextract
import stopit

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
        prompt_user_input_login: bool = True,
        login_prompt_callback: Optional[Callable[[str], None]] = None,
        login_prompt_timeout_seconds: Optional[float] = None
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

        try:
            self.__internal_id = cookies_folder_path.strip(os.path.sep).split(os.path.sep)[-1]
        except:
            self.__internal_id = cookies_folder_path or self.browser.cookies_folder_path

        self.browser.get(self.home_url)

        try:
            self.did_log_in_at_init = self.login_via_cookies(
                prompt_user_input_login=prompt_user_input_login,
                login_prompt_callback=login_prompt_callback,
                login_prompt_timeout_seconds=login_prompt_timeout_seconds,
                save_cookies=True
            )
        except Exception as e:
            print(e)
            self.did_log_in_at_init = False
            # self.quit()


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

    @property
    def domain(self) -> str:
        if hasattr(self, '__domain'):
            return self.__domain

        self.__domain = tldextract.extract(self.home_url).domain

        return self.__domain

    @property
    def page_name(self) -> str:
        if hasattr(self, '__page_name'):
            return self.__page_name

        self.__page_name = self.domain.lower().title()

        return self.__page_name
    
    def time_out_error(self, custom_message: Optional[str] = None) -> TimeoutError:
        message = 'TimeoutError - {} - {} - Operation did time out.'.format(self.page_name, self.__internal_id)

        if custom_message:
            message += ' - {}'.format(custom_message)

        return TimeoutError(message)


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def login_via_cookies(
        self,
        prompt_user_input_login: bool = True,
        login_prompt_callback: Optional[Callable[[str], None]] = None,
        login_prompt_timeout_seconds: Optional[float] = None,
        save_cookies: bool = True
    ) -> bool:
        login_cookies_result = self.browser.login_via_cookies(self.home_url, None)
        login_actual_result = login_cookies_result and self.is_logged_in

        if not login_cookies_result:
            print('{} - {} - Could not log in via cookies.'.format(self.page_name, self.__internal_id))
        elif not login_actual_result:
            print('{} - {} - Did find cookies, but could not log in with them.'.format(self.page_name, self.__internal_id))

        if not login_actual_result:
            if prompt_user_input_login or login_prompt_callback is not None:
                def local_login_prompt_callback(message: str):
                    input(message)

                try:
                    self.__call_login_prompt_callback(
                        login_prompt_callback if login_prompt_callback is not None else local_login_prompt_callback,
                        timeout=login_prompt_timeout_seconds
                    )

                    return self.login_via_cookies(promt_user_input_login=False, save_cookies=save_cookies)
                except Exception as e:
                    print(e)

            print('{} - {} - Did not log in.'.format(self.page_name, self.__internal_id))

            return False

        print('{} - {} - Successfully logged in. Saving cookies.'.format(self.page_name, self.__internal_id))
        time.sleep(0.5)
        self.browser.get(self.home_url)
        time.sleep(0.5)
        self.save_cookies()

        return True

    def save_cookies(self) -> None:
        self.browser.save_cookies()

    def quit(self) -> None:
        try:
            self.browser.driver.quit()
        except:
            pass


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @stopit.signal_timeoutable(default=self.time_out_error('Logging in'), timeout_param='timeout')
    def __call_login_prompt_callback(
        self,
        login_prompt_callback: Callable[[srt], None],
        timeout: float = None
    ) -> None:
        message = '{} - {} - Needs login.'.format(self.page_name, self.__internal_id)

        if timeout:
            message += ' (Timeout: {}s)'.format(self.__seconds_to_time_str(timeout))

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