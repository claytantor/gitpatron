var issue_share = document.getElementById("issue_share");
var issue_id = issue_share.getAttribute("issue-id");
var iframe = document.createElement('iframe');
iframe.src="https://qa.gitpatron.com/widget/issue/"+issue_id+"/";
iframe.width=210
iframe.height=360
iframe.frameBorder=0
issue_share.appendChild(iframe);



