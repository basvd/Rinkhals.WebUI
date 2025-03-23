
const callback = (mutationList, observer) => {
  for (const mutation of mutationList) {
    const inputs = document.querySelectorAll('input[name="color"]');
    if (inputs.length > 0)
    {
      // console.log(inputs);
    }
    for (const input of inputs) {
      input.setAttribute("type", "color");
    }
  }
};

const observer = new MutationObserver(callback);
const config = { childList: true, subtree: true };
observer.observe(document, config);
