
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "bytehunters-verify",
    title: "Verify with ByteHunters",
    contexts: ["selection"] //this option will only show when text is selected
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "bytehunters-verify") {
    const text = info.selectionText;
    
    //todo - create a prefilling api route in feature
    
    chrome.tabs.create({ 
      url: "http://127.0.0.1:5000/input" 
    });
  }
});