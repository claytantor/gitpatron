var issue_share = document.getElementById("issue_share_{{issue_id}}");
var iframe = document.createElement('iframe');
iframe.src="{{application_url}}/widget/issue/{{issue_id}}/";
iframe.width=210
iframe.height=360
iframe.frameBorder=0
issue_share.appendChild(iframe);