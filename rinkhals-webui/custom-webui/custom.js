
const callback = (mutationList, observer) => {
  for (const mutation of mutationList) {
    const inputs = document.querySelectorAll('input[name="color"]');
    for (const input of inputs) {
      input.setAttribute("type", "color");
    }
  }
};

const observer = new MutationObserver(callback);
const config = { childList: true, subtree: true };
observer.observe(document, config);
