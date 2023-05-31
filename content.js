document.addEventListener('keydown', function(event) {
  // 检查是否按下了 Ctrl + N 快捷键
  if (event.ctrlKey && event.key === 'i') {
    // 获取用户选择的文本
    let selection = window.getSelection();
    let selectedText = selection.toString();

    // 在页面上创建一个新的div元素，用作弹出窗口
    let popup = document.createElement('div');
    popup.classList.add('custom-popup'); // 添加一个自定义的类名
    popup.style.position = 'fixed';
    popup.style.left = '50%';
    popup.style.top = '50%';
    popup.style.transform = 'translate(-50%, -50%)';
    popup.style.backgroundColor = 'white';
    popup.style.padding = '20px';
    popup.style.border = '1px solid black';
    popup.style.zIndex = '1000';
    popup.style.width = '50%';
    popup.style.height = '50%';
    popup.style.overflowY = 'scroll'; // 仅显示垂直滚动条
    popup.style.overflowX = 'hidden'; // 隐藏水平滚动条
    popup.style.wordWrap = 'break-word'; // 达到宽度后换行
    popup.classList.add('draggable'); // 添加拖动功能

    // 创建一个关闭按钮
    let closeButton = document.createElement('button');
    closeButton.textContent = 'Close';
    closeButton.onclick = function() {
      // 通过类名查找关闭按钮所在的弹出窗口，并移除它
      let popup = document.querySelector('.custom-popup');
      if (popup) {
        document.body.removeChild(popup);
      }
    };
    popup.appendChild(closeButton);

    // 创建一个<pre>元素来显示文本
    let pre = document.createElement('pre');
    popup.appendChild(pre);

    // 创建 AJAX 请求
    fetch('http://127.0.0.1:5000/process-text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: selectedText })
    })
      .then(response => response.json())
      .then(data => {
        // 处理从服务器端返回的数据
        console.log(data);
        // 在弹出窗口中显示处理后的结果
        let result = document.createElement('pre');
        result.innerHTML = data.result;
        let popup = document.querySelector('.custom-popup');
        popup.appendChild(result);

        // 初始化拖动功能
        let draggableElements = document.querySelectorAll('.custom-popup');
        draggableElements.forEach(function(element) {
          let offsetX, offsetY;
          element.addEventListener('mousedown', function(event) {
            offsetX = event.clientX - element.offsetLeft;
            offsetY = event.clientY - element.offsetTop;
            element.style.cursor = 'grabbing';
          });
          document.addEventListener('mousemove', function(event) {
            if (element.style.cursor === 'grabbing') {
              let left = event.clientX - offsetX;
              let top = event.clientY - offsetY;
              element.style.left = left + 'px';
              element.style.top = top + 'px';
            }
          });
          element.addEventListener('mouseup', function() {
            element.style.cursor = 'grab';
          });
        });
      })
      .catch(error => {
        console.error(error);
      });

    // 创建一个调整器
    let resizer = document.createElement('div');
    resizer.style.width = '10px';
    resizer.style.height = '10px';
    resizer.style.background = 'black';
    resizer.style.position = 'absolute';
    resizer.style.right = '0';
    resizer.style.bottom = '0';
    resizer.style.cursor = 'nwse-resize';
    popup.appendChild(resizer);

    // 使调整器可以拖动以改变窗口的大小
    let startX, startY, startWidth, startHeight;
    resizer.addEventListener('mousedown', e => {
      startX = e.clientX;
      startY = e.clientY;
      startWidth = parseFloat(getComputedStyle(popup, null).width.replace("px", ""));
      startHeight = parseFloat(getComputedStyle(popup, null).height.replace("px", ""));
      document.addEventListener('mousemove', resize);
      document.addEventListener('mouseup', stopResize);
    });

    let resize = e => {
      popup.style.width = startWidth + (e.clientX - startX) + 'px';
      popup.style.height = startHeight + (e.clientY - startY) + 'px';
    }

    let stopResize = () => {
      document.removeEventListener('mousemove', resize);
    }
    
     // 创建切换主题的按钮
     let lightModeButton = document.createElement('button');
     lightModeButton.textContent = 'Light Mode';
     lightModeButton.onclick = function() {
       popup.style.backgroundColor = 'white';
       popup.style.color = 'black';
     };
     popup.appendChild(lightModeButton);
 
     let darkModeButton = document.createElement('button');
     darkModeButton.textContent = 'Dark Mode';
     darkModeButton.onclick = function() {
       popup.style.backgroundColor = '#282a36'; // 替换为深灰色背景
       popup.style.color = '#f8f8f2'; // 替换为淡灰色文字
     };
     popup.appendChild(darkModeButton);

    
    // 将弹出窗口添加到页面中
    document.body.appendChild(popup);

    // 防止触发浏览器的默认行为
    event.preventDefault();
  }
});
