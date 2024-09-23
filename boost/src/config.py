from typing import Optional, Generic, TypeVar, List, Union, Type, Dict
import os

T = TypeVar('T')


class ConfigDict(Dict[str, Union[str, int, float, bool]]):

  @classmethod
  def from_string(cls, value: str) -> 'ConfigDict':
    result = cls()
    if not value:
      return result
    pairs = value.split(',')
    for pair in pairs:
      key, val = pair.split('=')
      key = key.strip()
      val = val.strip()
      # Try to parse the value as int, float, or bool
      if val.lower() == 'true':
        result[key] = True
      elif val.lower() == 'false':
        result[key] = False
      else:
        try:
          result[key] = int(val)
        except ValueError:
          try:
            result[key] = float(val)
          except ValueError:
            result[key] = val
    return result


class StrList(List[str]):

  @classmethod
  def from_string(cls, value: str) -> 'StrList':
    return cls(item.strip() for item in value.split(';') if item.strip()
              ) if value.strip() else cls()


class IntList(List[int]):

  @classmethod
  def from_string(cls, value: str) -> 'IntList':
    return cls(int(item.strip()) for item in value.split(';') if item.strip()
              ) if value.strip() else cls()


class FloatList(List[float]):

  @classmethod
  def from_string(cls, value: str) -> 'FloatList':
    return cls(
      float(item.strip()) for item in value.split(';') if item.strip()
    ) if value.strip() else cls()


class BoolList(List[bool]):

  @classmethod
  def from_string(cls, value: str) -> 'BoolList':
    return cls(
      item.strip().lower() == 'true'
      for item in value.split(';')
      if item.strip()
    ) if value.strip() else cls()


class Config(Generic[T]):
  name: str
  type: Type[T]
  default: str
  description: Optional[str]
  __value__: T

  def __init__(
    self,
    name: str,
    type: Type[T],
    default: str,
    description: Optional[str] = None
  ):
    self.name = name
    self.type = type
    self.default = default
    self.description = description
    self.__value__ = self.resolve_value()

  @property
  def value(self) -> T:
    return self.__value__

  def resolve_value(self) -> Union[T, List[T]]:
    if '*' in self.name:
      return self._resolve_wildcard()
    else:
      return self._resolve_single()

  def _resolve_single(self) -> T:
    raw_value = os.getenv(self.name, self.default)
    if isinstance(raw_value, list):
      raw_value = raw_value[0] if raw_value else ''
    return self._convert_value(raw_value)

  def _resolve_wildcard(self) -> List[T]:
    prefix = self.name.replace('*', '')
    matching_vars = [
      (key, value)
      for key, value in os.environ.items()
      if key.startswith(prefix)
    ]

    if not matching_vars:
      if isinstance(self.default, str):
        return [self._convert_value(self.default)] if self.default else []
      return self.default

    return [self._convert_value(value) for _, value in sorted(matching_vars)]

  def _convert_value(self, value: str) -> T:
    if issubclass(
      self.type, (StrList, IntList, FloatList, BoolList, ConfigDict)
    ):
      return self.type.from_string(value)
    elif self.type == str:
      return value
    elif self.type == int:
      return int(value)
    elif self.type == float:
      return float(value)
    elif self.type == bool:
      return value.lower() in ('true', '1', 'yes', 'on')
    else:
      return self.type(value)


# ----------------- APIs -----------------

HARBOR_OPENAI_URLS = Config[StrList](
  name='HARBOR_OPENAI_URLS',
  type=StrList,
  default='',
  description='A list of URLs to the OpenAI APIs'
)

HARBOR_OPENAI_KEYS = Config[StrList](
  name='HARBOR_OPENAI_KEYS',
  type=StrList,
  default='',
  description='A list of API keys to use for the OpenAI APIs'
)

HARBOR_BOOST_OPENAI_URLS = Config[StrList](
  name='HARBOR_BOOST_OPENAI_URLS',
  type=StrList,
  default='',
  description='A list of URLs to the OpenAI APIs to boost'
)

HARBOR_BOOST_OPENAI_KEYS = Config[StrList](
  name='HARBOR_BOOST_OPENAI_KEYS',
  type=StrList,
  default='',
  description='A list of API keys to use for the OpenAI APIs to boost'
)

HARBOR_BOOST_EXTRA_OPENAI_URLS = Config[str](
  name='HARBOR_BOOST_OPENAI_URL_*',
  type=str,
  default='',
  description='Named OpenAI-compatible API URLs to boost'
)

HARBOR_BOOST_EXTRA_OPENAI_KEYS = Config[str](
  name='HARBOR_BOOST_OPENAI_KEY_*',
  type=str,
  default='',
  description=
  'Named OpenAI-compatible API keys to use for the OpenAI APIs to boost'
)

# Combining all the sources from
# above into a single list
HARBOR_BOOST_APIS = [
  *HARBOR_OPENAI_URLS.value, *HARBOR_BOOST_OPENAI_URLS.value,
  *HARBOR_BOOST_EXTRA_OPENAI_URLS.value
]

HARBOR_BOOST_KEYS = [
  *HARBOR_OPENAI_KEYS.value, *HARBOR_BOOST_OPENAI_KEYS.value,
  *HARBOR_BOOST_EXTRA_OPENAI_KEYS.value
]

# ----------------- MODULES -----------------

HARBOR_BOOST_MODULES = Config[StrList](
  name='HARBOR_BOOST_MODULES',
  type=StrList,
  default='',
  description='A list of boost modules to load'
)

# ----------------- KLMBR -----------------

HARBOR_BOOST_KLMBR_PERCENTAGE = Config[int](
  name='HARBOR_BOOST_KLMBR_PERCENTAGE',
  type=int,
  default='15',
  description='The percentage of text to modify with the klmbr module'
)

HARBOR_BOOST_KLMBR_MODS = Config[StrList](
  name='HARBOR_BOOST_KLMBR_MODS',
  type=StrList,
  default='',
  description=f'The list of modifications klmbr will apply'
)

HARBOR_BOOST_KLMBR_STRAT = Config[str](
  name='HARBOR_BOOST_KLMBR_STRAT',
  type=str,
  default='all',
  description='The strategy that selects messages to modify for the klmbr module'
)

HARBOR_BOOST_KLMBR_STRAT_PARAMS = Config[ConfigDict](
  name='HARBOR_BOOST_KLMBR_STRAT_PARAMS',
  type=ConfigDict,
  default='',
  description=
  'The parameters for the strategy that selects messages to modify for the klmbr module'
)

# ----------------- RCN -----------------

HARBOR_BOOST_RCN_STRAT = Config[str](
  name='HARBOR_RCN_STRAT',
  type=str,
  default='match',
  description='The strategy that selects messages to modify for the rcn module'
)

HARBOR_BOOST_RCN_STRAT_PARAMS = Config[ConfigDict](
  name='HARBOR_RCN_STRAT',
  type=ConfigDict,
  # Default - last user message
  default='role=user,index=-1',
  description=
  'The parameters for the strategy that selects messages to modify for the rcn module'
)

# ----------------- G1 -----------------

HARBOR_BOOST_G1_STRAT = Config[str](
  name='HARBOR_G1_STRAT',
  type=str,
  default='match',
  description='The strategy that selects messages to modify for the g1 module'
)

HARBOR_BOOST_G1_STRAT_PARAMS = Config[ConfigDict](
  name='HARBOR_G1_STRAT_PARAMS',
  type=ConfigDict,
  # Default - last user message
  default='role=user,index=-1',
  description=
  'The parameters for the strategy that selects messages to modify for the g1 module'
)

HARBOR_BOOST_G1_MAX_STEPS = Config[int](
  name='HARBOR_G1_MAX_STEPS',
  type=int,
  default='15',
  description='The maximum number of reasoning steps to generate'
)