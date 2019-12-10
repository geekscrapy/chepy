from pkg_resources import resource_filename

import ujson
import regex as re
import jsonpath_rw
from urllib.parse import urlparse as _pyurlparse
from parsel import Selector
from ..core import ChepyCore, ChepyDecorators


class Extractors(ChepyCore):
    def _parsel_obj(self):
        """Returns a parsel.Selector object
        """
        return Selector(self._convert_to_str())

    @ChepyDecorators.call_stack
    def extract_strings(self, length: int = 4):
        """Extract strings from state
        
        Args:
            length (int, optional): Min length of string. Defaults to 4.
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> Chepy("tests/files/hello").load_file().extract_strings().o
            [
                b'__PAGEZERO',
                b'__TEXT',
                b'__text',
                b'__TEXT',
                b'__stubs',
                b'__TEXT',
                ...
            ]
        """
        pattern = b"[^\x00-\x1F\x7F-\xFF]{" + str(length).encode() + b",}"
        self.state = re.findall(pattern, self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def extract_ips(self, invalid: bool = False, is_binary: bool = False):
        """Extract ipv4 and ipv6 addresses
        
        Args:
            invalid (bool, optional): Include :: addresses. Defaults to False.
            is_binary (bool, optional): The state is in binary format. It will then first 
                extract the strings from it before matching.
        
        Returns:
            Chepy: The Chepy object. 
        """
        pattern = b"((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))"
        if is_binary:  # pragma: no cover
            matched = list(
                filter(lambda x: re.search(pattern, x), self.extract_strings().o)
            )
        else:
            matched = list(
                filter(
                    lambda x: re.search(pattern, x), self._convert_to_bytes().split()
                )
            )
        self.state = matched
        return self

    @ChepyDecorators.call_stack
    def extract_email(self, is_binary: bool = False):
        """Extract email

        Args:
            is_binary (bool, optional): The state is in binary format. It will then first 
                extract the strings from it before matching.
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            Sometimes, the state is in a binary format, and not readable. In this case 
            set the binary flag to True.

            >>> Chepy("tests/files/test.der").load_file().extract_email(is_binary=True).o
        """
        pattern = b"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if is_binary:
            matched = list(
                filter(lambda x: re.search(pattern, x), self.extract_strings().o)
            )
        else:  # pragma: no cover
            matched = list(
                filter(
                    lambda x: re.search(pattern, x), self._convert_to_bytes().split()
                )
            )
        self.state = matched
        return self

    @ChepyDecorators.call_stack
    def extract_mac_address(self, is_binary: bool = False):
        """Extract MAC addresses

        Args:
            is_binary (bool, optional): The state is in binary format. It will then first 
                extract the strings from it before matching.
        
        Returns:
            Chepy: The Chepy object. 
        """
        pattern = b"^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$"
        if is_binary:  # pragma: no cover
            matched = list(
                filter(lambda x: re.search(pattern, x), self.extract_strings().o)
            )
        else:
            matched = list(
                filter(
                    lambda x: re.search(pattern, x), self._convert_to_bytes().split()
                )
            )
        self.state = matched
        return self

    @ChepyDecorators.call_stack
    def extract_urls(self, is_binary: bool = False):
        """Extract urls including http, file, ssh and ftp

        Args:
            is_binary (bool, optional): The state is in binary format. It will then first 
                extract the strings from it before matching.
        
        Returns:
            Chepy: The Chepy object. 
        """
        pattern = b"(file|ftps?|http[s]?|ssh)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        if is_binary:  # pragma: no cover
            matched = list(
                filter(lambda x: re.search(pattern, x), self.extract_strings().o)
            )
        else:
            matched = list(
                filter(
                    lambda x: re.search(pattern, x), self._convert_to_bytes().split()
                )
            )
        self.state = matched
        return self

    @ChepyDecorators.call_stack
    def extract_domains(self, is_binary: bool = False):
        """Extract domains

        Args:
            is_binary (bool, optional): The state is in binary format. It will then first 
                extract the strings from it before matching.
        
        Returns:
            Chepy: The Chepy object. 
        """
        if is_binary:  # pragma: no cover
            matched = list(_pyurlparse(x).netloc for x in self.extract_strings().o)
        else:
            matched = list(
                _pyurlparse(x).netloc
                for x in self._convert_to_bytes().split()
                if x.startswith(b"http")
            )
        self.state = matched
        return self

    @ChepyDecorators.call_stack
    def xpath_selector(self, query: str, namespaces: str = None):
        """Extract data using valid xpath selectors
        
        Args:
            query (str): Required. Xpath query
            namespaces (str, optional): Namespace. Applies for XML data. Defaults to None.
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> c = Chepy("http://example.com")
            >>> c.http_request()
            >>> c.xpath_selector("//title/text()")
            >>> c.get_by_index(0)
            >>> c.o
            "Example Domain"
        """
        self.state = (
            Selector(self._convert_to_str(), namespaces=namespaces)
            .xpath(query)
            .getall()
        )
        return self

    @ChepyDecorators.call_stack
    def css_selector(self, query: str):
        """Extract data using valid CSS selectors
        
        Args:
            query (str): Required. CSS query
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> c = Chepy("http://example.com")
            >>> c.http_request()
            >>> c.css_selector("title")
            >>> c.get_by_index(0)
            >>> c.o
            "<title>Example Domain</title>"
        """
        self.state = self._parsel_obj().css(query).getall()
        return self

    @ChepyDecorators.call_stack
    def jpath_selector(self, query: str):
        """Query JSON with jpath query

        `Reference <https://goessner.net/articles/JsonPath/index.html#e2>`__
        
        Args:
            query (str): Required. Query. For reference, see the help
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> c = Chepy("tests/files/test.json")
            >>> c.load_file()
            >>> c.jpath_selector("[*].name.first")
            >>> c.get_by_index(2)
            >>> c.o
            "Long"
        """
        self.state = list(
            j.value
            for j in jsonpath_rw.parse(query).find(ujson.loads(self._convert_to_str()))
        )
        return self

    @ChepyDecorators.call_stack
    def html_comments(self):
        """Extract html comments
        
        Returns:
            Chepy: The Chepy object. 
        """
        self.state = list(
            filter(lambda x: x != "", self._parsel_obj().xpath("//comment()").getall())
        )
        return self

    @ChepyDecorators.call_stack
    def js_comments(self):
        """Extract javascript comments

        Some false positives is expected because of inline // comments
        
        Returns:
            Chepy: The Chepy object. 
        """
        self.state = re.findall(
            r"/\*[\w'\s\r\n\*]*\*/|//[\w\s']*|/\*.+?\*/", self._convert_to_str()
        )
        return self

    @ChepyDecorators.call_stack
    def html_tags(self, tag: str):
        """Extract tags from html along with their attributes
        
        Args:
            tag (str): A HTML tag
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> Chepy("http://example.com").http_request().html_tags('p').o
            [
                {'tag': 'p', 'attributes': {}},
                {'tag': 'p', 'attributes': {}},
                {'tag': 'p', 'attributes': {}}
            ]
        """
        tags = []

        for element in self._parsel_obj().xpath("//{}".format(tag)):
            attributes = []
            for index, attribute in enumerate(element.xpath("@*"), start=1):
                attribute_name = element.xpath("name(@*[%d])" % index).extract_first()
                attributes.append((attribute_name, attribute.extract()))
            tags.append({"tag": tag, "attributes": dict(attributes)})

        self.state = tags
        return self

    @ChepyDecorators.call_stack
    def secrets(self):  # pragma: no cover
        """Checks for secrets 
        
        Checks ~1500 different secrets patterns. Returns a dict of partial 
        pattern name as the key, and and array of found matches as the value. 
        This mostly checks for common variable names that contains secrets. 
        
        Returns:
            Chepy: The Chepy object. 
        """
        found = {}
        secrets_path = resource_filename(__name__, "internal/data/secrets.txt")
        with open(secrets_path, "r") as f:
            for pattern in f:
                matches = re.findall(fr"{pattern}.*?".strip(), self.response.text)
                if matches:
                    found[re.sub(r"[^a-zA-Z0-9_]", "", pattern[0:20])] = matches
        self.state = found
        return self
