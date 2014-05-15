declui = {};

declui.template = {};

declui.template.List = function(templateArray) {
  this.templateArray = templateArray;
};
declui.template.List.prototype.generate = function(state) {
  var domArray = [];
  for (var i = 0; i < this.templateArray.length; i++) {
    domArray.push(this.templateArray[i].generate(state));
  }
  return new declui.dom.List(domArray);
};

declui.template.Div = function(templateList) {
  this.templateList = templateList;
};
declui.template.Div.prototype.generate = function(state) {
  return new declui.dom.Div(this.templateList.generate(state));
};

declui.template.If = function(boolTest, templateListTrue, templateListFalse) {
  this.boolTest = boolTest;
  this.templateListTrue = templateListTrue;
  this.templateListFalse = templateListFalse;
};
declui.template.If.prototype.generate = function(state) {
  var boolResult = this.boolTest(state);
  return new declui.dom.If(this.boolTest, this.templateListTrue,
      this.templateListFalse, boolResult,
      (boolResult ? this.templateListTrue : this.templateListFalse).
          generate(state));
};

declui.template.Val = function(expression) {
  this.expression = expression;
};
declui.template.Val.prototype.generate = function(state) {
  return new declui.dom.Val(this.expression, this.expression(state));
};

declui.template.Text = function(string) {
  this.string = string;
};
declui.template.Text.prototype.generate = function(state) {
  return new declui.dom.Text(this.string);
};


declui.dom = {}

declui.dom.List = function(domArray) {
  this.domArray = domArray;

  this.nodeList = [];
  for (var i = 0; i < this.domArray.length; i++) {
    Array.prototype.push.apply(this.nodeList, this.domArray[i].nodeList);
  }
};
declui.dom.List.prototype.mutate = function(state, container, lastChildNode) {
  this.nodeList = [];
  for (var i = 0; i < this.domArray.length; i++) {
    lastChildNode = this.domArray[i].mutate(state, container, lastChildNode);
    Array.prototype.push.apply(this.nodeList, this.domArray[i].nodeList);
  }

  return lastChildNode;
};

declui.dom.Div = function(domList) {
  this.domList = domList;
  this.divElement = document.createElement('div');
  for (var i = 0; i < this.domList.nodeList.length; i++) {
    this.divElement.appendChild(this.domList.nodeList[i]);
  }

  this.nodeList = [this.divElement];
};
declui.dom.Div.prototype.mutate = function(state, container, lastChildNode) {
  this.domList.mutate(state, this.divElement, null);
  return this.divElement;
};

declui.dom.If = function(boolTest, templateListTrue, templateListFalse,
    currentBoolResult, domList) {
  this.boolTest = boolTest;
  this.templateListTrue = templateListTrue;
  this.templateListFalse = templateListFalse;
  this.currentBoolResult = currentBoolResult;
  this.domList = domList;

  this.nodeList = this.domList.nodeList;
};
declui.dom.If.prototype.mutate = function(state, container, lastChildNode) {
  var boolResult = this.boolTest(state);
  if (boolResult == this.currentBoolResult) {
    this.domList.mutate(state, container, lastChildNode);
  } else {
    this.currentBoolResult = boolResult;
    this.domList =
        (boolResult ? this.templateListTrue : this.templateListFalse)
            .generate(state);
    for (var i = 0; i < this.nodeList.length; i++) {
      container.removeChild(this.nodeList[i]);
    }
    var childToInsertBefore =
        lastChildNode ? lastChildNode.nextSibling : container.firstChild;
    this.nodeList = this.domList.nodeList;
    for (var i = 0; i < this.nodeList.length; i++) {
      container.insertBefore(this.nodeList[i], childToInsertBefore);
    }
  }
  return this.domList.nodeList[this.domList.nodeList.length - 1]
};

declui.dom.Val = function(expression, string) {
  this.node = document.createTextNode(string)
  this.expression = expression;

  this.nodeList = [this.node];
};
declui.dom.Val.prototype.mutate = function(state, container, lastChildNode) {
  this.node.textContent = this.expression(state);
  return this.nodeList[0];
};

declui.dom.Text = function(string) {
  this.nodeList = [document.createTextNode(string)];
};
declui.dom.Text.prototype.mutate = function(state, container, lastChildNode) {
  return this.nodeList[0];
};

declui.global = {};
declui.global.domList;
declui.global.initialize = function(templateList, state) {
  window.onload = function() {
    declui.global.domList = templateList.generate(state);
    for (var i = 0; i < declui.global.domList.nodeList.length; i++) {
      document.body.appendChild(declui.global.domList.nodeList[i]);
    }
  };
}
declui.global.mutate = function(state) {
  declui.global.domList.mutate(state, document.body, null);
}
