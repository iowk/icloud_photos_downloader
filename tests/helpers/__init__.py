import glob
import os
import shutil
import traceback
from typing import List, Protocol, Sequence, Tuple, TypeVar

import vcr
from click.testing import CliRunner, Result
from icloudpd.base import main
from pyicloud_ipd.base import PyiCloudService


def print_result_exception(result: Result) -> None:
    ex = result.exception
    if ex:
        # This only works on Python 3
        if hasattr(ex, "__traceback__"):
            traceback.print_exception(type(ex), value=ex, tb=ex.__traceback__)
        else:
            print(ex)


def path_from_project_root(file_name: str) -> str:
    parent = os.path.relpath(os.path.dirname(file_name), "./")
    return parent


def recreate_path(path_name: str) -> None:
    """Removes if exists and creates dir"""
    if os.path.exists(path_name):
        shutil.rmtree(path_name)
    os.makedirs(path_name)


def create_files(data_dir: str, files_to_create: Sequence[Tuple[str, str, int]]) -> None:
    for dir_name, file_name, file_size in files_to_create:
        normalized_dir_name = os.path.normpath(dir_name)
        os.makedirs(os.path.join(data_dir, normalized_dir_name), exist_ok=True)
        with open(os.path.join(data_dir, normalized_dir_name, file_name), "a") as f:
            f.truncate(file_size)


# TypeVar to parameterize for specific types
# _SA = TypeVar('_SA', bound='SupportsAdd')

# class SupportsAdd(Protocol):
#     """Any type T where +(:T, :T) -> T"""
#     def __add__(self: _SA, other: _SA) -> _SA: ...

# class IterableAdd(SupportsAdd, Iterable, Protocol): ...


def combine_file_lists(
    files_to_create: Sequence[Tuple[str, str, int]], files_to_download: List[Tuple[str, str]]
) -> Sequence[Tuple[str, str]]:
    return (
        [(dir_name, file_name) for (dir_name, file_name, _) in files_to_create]
    ) + files_to_download


_T = TypeVar("_T")


class AssertEquality(Protocol):
    def __call__(self, __first: _T, __second: _T, __msg: str) -> None: ...


def assert_files(
    assert_equal: AssertEquality, data_dir: str, files_to_assert: Sequence[Tuple[str, str]]
) -> None:
    files_in_result = glob.glob(os.path.join(data_dir, "**/*.*"), recursive=True)

    assert_equal(sum(1 for _ in files_in_result), len(files_to_assert), "File count does not match")

    for dir_name, file_name in files_to_assert:
        normalized_dir_name = os.path.normpath(dir_name)
        file_path = os.path.join(normalized_dir_name, file_name)
        assert_equal(
            os.path.exists(os.path.join(data_dir, file_path)),
            True,
            f"File {file_path} expected, but does not exist",
        )


def run_cassette(cassette_path: str, params: Sequence[str]) -> Result:
    with vcr.use_cassette(cassette_path):
        # Pass fixed client ID via environment variable
        runner = CliRunner(env={"CLIENT_ID": "DE309E26-942E-11E8-92F5-14109FE0B321"})
        result = runner.invoke(
            main,
            params,
        )
        print_result_exception(result)
        return result


def run_icloudpd_test(
    assert_equal: AssertEquality,
    vcr_path: str,
    base_dir: str,
    cassette_filename: str,
    files_to_create: Sequence[Tuple[str, str, int]],
    files_to_download: List[Tuple[str, str]],
    params: List[str],
) -> Tuple[str, Result]:
    cookie_dir = os.path.join(base_dir, "cookie")
    data_dir = os.path.join(base_dir, "data")

    for dir in [base_dir, cookie_dir, data_dir]:
        recreate_path(dir)

    create_files(data_dir, files_to_create)

    result = run_cassette(
        os.path.join(vcr_path, cassette_filename),
        [
            "-d",
            data_dir,
            "--cookie-directory",
            cookie_dir,
        ]
        + params,
    )

    files_to_assert = combine_file_lists(files_to_create, files_to_download)
    assert_files(assert_equal, data_dir, files_to_assert)

    return (data_dir, result)


def mocked_load_session_data(self: PyiCloudService) -> None:
    self.session_data = {
        "client_id": "DE309E26-942E-11E8-92F5-14109FE0B321",
        "scnt": "scnt-1234567890",
        "account_country": "USA",
        "session_id": "sess-1234567890",
        "session_token": "token-1234567890",
        "trust_eligible": "true",
    }


mocked_icloud_data = {
    "dsInfo": {
        "lastName": "Doe",
        "iCDPEnabled": False,
        "tantorMigrated": False,
        "dsid": "12345678901",
        "hsaEnabled": True,
        "ironcadeMigrated": True,
        "locale": "en-us_US",
        "brZoneConsolidated": False,
        "ICDRSCapableDeviceList": "",
        "isManagedAppleID": False,
        "isCustomDomainsFeatureAvailable": True,
        "isHideMyEmailFeatureAvailable": True,
        "ContinueOnDeviceEligibleDeviceInfo": [],
        "gilligan-invited": True,
        "appleIdAliases": [],
        "hsaVersion": 1,
        "ubiquityEOLEnabled": True,
        "isPaidDeveloper": False,
        "countryCode": "USA",
        "notificationId": "12341234-1234-12341234-1234",
        "primaryEmailVerified": True,
        "aDsID": "123456-12-12345678-1234-1234-1234-123456789012",
        "locked": False,
        "ICDRSCapableDeviceCount": 0,
        "hasICloudQualifyingDevice": False,
        "primaryEmail": "jdoe@gmail.com",
        "appleIdEntries": [{"isPrimary": True, "type": "EMAIL", "value": "jdoe@gmail.com"}],
        "gilligan-enabled": True,
        "isWebAccessAllowed": True,
        "fullName": "John Doe",
        "mailFlags": {
            "isThreadingAvailable": False,
            "isSearchV2Provisioned": False,
            "rawBits": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
            "isCKMail": False,
            "isMppSupportedInCurrentCountry": True,
        },
        "languageCode": "en-us",
        "appleId": "jdoe@gmail.com",
        "analyticsOptInStatus": False,
        "firstName": "john",
        "iCloudAppleIdAlias": "",
        "notesMigrated": True,
        "beneficiaryInfo": {"isBeneficiary": False},
        "hasPaymentInfo": True,
        "pcsDeleted": False,
        "appleIdAlias": "",
        "brMigrated": True,
        "statusCode": 2,
        "familyEligible": True,
    },
    "hasMinimumDeviceForPhotosWeb": True,
    "iCDPEnabled": False,
    "webservices": {
        "reminders": {"url": "https://p61-remindersws.icloud.com:443", "status": "active"},
        "ckdatabasews": {
            "pcsRequired": True,
            "url": "https://p61-ckdatabasews.icloud.com:443",
            "status": "active",
        },
        "photosupload": {
            "pcsRequired": True,
            "url": "https://p61-uploadphotosws.icloud.com:443",
            "status": "active",
        },
        "photos": {
            "pcsRequired": True,
            "uploadUrl": "https://p61-uploadphotosws.icloud.com:443",
            "url": "https://p61-photosws.icloud.com:443",
            "status": "active",
        },
        "drivews": {
            "pcsRequired": True,
            "url": "https://p61-drivews.icloud.com:443",
            "status": "active",
        },
        "uploadimagews": {
            "url": "https://p61-uploadimagews.icloud.com:443",
            "status": "active",
        },
        "schoolwork": {},
        "cksharews": {"url": "https://p61-ckshare.icloud.com:443", "status": "active"},
        "findme": {"url": "https://p61-fmipweb.icloud.com:443", "status": "active"},
        "ckdeviceservice": {"url": "https://p61-ckdevice.icloud.com:443"},
        "iworkthumbnailws": {
            "url": "https://p61-iworkthumbnailws.icloud.com:443",
            "status": "active",
        },
        "mccgateway": {"url": "https://p61-mccgateway.icloud.com:443", "status": "active"},
        "calendar": {
            "isMakoAccount": False,
            "url": "https://p61-calendarws.icloud.com:443",
            "status": "active",
        },
        "docws": {
            "pcsRequired": True,
            "url": "https://p61-docws.icloud.com:443",
            "status": "active",
        },
        "settings": {"url": "https://p61-settingsws.icloud.com:443", "status": "active"},
        "premiummailsettings": {
            "url": "https://p61-maildomainws.icloud.com:443",
            "status": "active",
        },
        "ubiquity": {"url": "https://p61-ubiquityws.icloud.com:443", "status": "active"},
        "keyvalue": {"url": "https://p61-keyvalueservice.icloud.com:443", "status": "active"},
        "mpp": {"url": "https://relay.icloud-mpp.com", "status": "active"},
        "archivews": {"url": "https://p61-archivews.icloud.com:443", "status": "active"},
        "push": {"url": "https://p61-pushws.icloud.com:443", "status": "active"},
        "iwmb": {"url": "https://p61-iwmb.icloud.com:443", "status": "active"},
        "iworkexportws": {
            "url": "https://p61-iworkexportws.icloud.com:443",
            "status": "active",
        },
        "sharedlibrary": {"url": "https://sharedlibrary.icloud.com:443", "status": "active"},
        "geows": {"url": "https://p61-geows.icloud.com:443", "status": "active"},
        "account": {
            "iCloudEnv": {"shortId": "p", "vipSuffix": "prod"},
            "url": "https://p61-setup.icloud.com:443",
            "status": "active",
        },
        "contacts": {"url": "https://p61-contactsws.icloud.com:443", "status": "active"},
        "developerapi": {"url": "https://developer-api.icloud.com:443", "status": "active"},
    },
    "pcsEnabled": True,
    "configBag": {
        "urls": {
            "accountCreateUI": "https://appleid.apple.com/widget/account/?widgetKey=#!create",
            "accountLoginUI": "https://idmsa.apple.com/appleauth/auth/signin?widgetKey=",
            "accountLogin": "https://setup.icloud.com/setup/ws/1/accountLogin",
            "accountRepairUI": "https://appleid.apple.com/widget/account/?widgetKey=#!repair",
            "downloadICloudTerms": "https://setup.icloud.com/setup/ws/1/downloadLiteTerms",
            "repairDone": "https://setup.icloud.com/setup/ws/1/repairDone",
            "accountAuthorizeUI": "https://idmsa.apple.com/appleauth/auth/authorize/signin?client_id=",
            "vettingUrlForEmail": "https://id.apple.com/IDMSEmailVetting/vetShareEmail",
            "accountCreate": "https://setup.icloud.com/setup/ws/1/createLiteAccount",
            "getICloudTerms": "https://setup.icloud.com/setup/ws/1/getTerms",
            "vettingUrlForPhone": "https://id.apple.com/IDMSEmailVetting/vetSharePhone",
        },
        "accountCreateEnabled": True,
    },
    "hsaTrustedBrowser": True,
    "appsOrder": [
        "mail",
        "contacts",
        "calendar",
        "photos",
        "iclouddrive",
        "notes3",
        "reminders",
        "pages",
        "numbers",
        "keynote",
        "newspublisher",
        "find",
        "settings",
    ],
    "version": 2,
    "isExtendedLogin": True,
    "pcsServiceIdentitiesIncluded": False,
    "hsaChallengeRequired": False,
    "requestInfo": {"country": "US", "timeZone": "EST", "region": "NC"},
    "pcsDeleted": False,
    "iCloudInfo": {"SafariBookmarksHasMigratedToCloudKit": False},
    "apps": {
        "calendar": {},
        "reminders": {},
        "keynote": {"isQualifiedForBeta": True},
        "settings": {"canLaunchWithOneFactor": True},
        "mail": {},
        "numbers": {"isQualifiedForBeta": True},
        "photos": {},
        "pages": {"isQualifiedForBeta": True},
        "notes3": {},
        "find": {"canLaunchWithOneFactor": True},
        "iclouddrive": {},
        "newspublisher": {"isHidden": True},
        "contacts": {},
    },
}
