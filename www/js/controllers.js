url_search = "gsearch.php?callback=JSON_CALLBACK&q="
url_down = "gdown.php?callback=JSON_CALLBACK&id="
url_base = "http://YOURDOMAIN/groove"

angular.module('starter.controllers', [])

.controller('AppCtrl', function($scope, $ionicModal, $timeout) {
  
})

.controller('SearchCtrl', function($scope, $http) {
  
 $scope.cordova = window.cordova
   $scope.random = function(){
   setTimeout(function(){
   if($scope.visible){ 
         $scope.start = 0
     $scope.end = $scope.start  + 10
    $scope.results = _.shuffle($scope.results)
    copydata = JSON.parse(JSON.stringify($scope.results))
    $scope.visible = copydata.splice($scope.start,$scope.end)
   }
    return $scope.$broadcast('scroll.refreshComplete');
  },100)
 
 }
  $scope.load = function(){
  

  setTimeout(function(){
  
  if($scope.visible){ 
    $scope.start = $scope.end
    $scope.end = $scope.start +10
    copydata = JSON.parse(JSON.stringify($scope.results))
    $scope.visible = _.union($scope.visible, copydata.splice($scope.start,$scope.end));
   }
    return $scope.$broadcast('scroll.infiniteScrollComplete');
  },2000)
  
  
  }
 $scope.exit = function(){
 
    if(navigator.app){
            navigator.app.exitApp();
    }else if(navigator.device){
            navigator.device.exitApp();
    }

 }
 $scope.search = function(q){
  $scope.searching = true
  $scope.last = q
   $http.jsonp(url_base+ "/" +url_search + q).success(function(data){
     if(data.errors){return $scope.errors = data.errors}
     $scope.results = data 
     $scope.start = 0
     $scope.end = $scope.start  + 10
     copydata = JSON.parse(JSON.stringify(data))
     $scope.visible = copydata.splice($scope.start,$scope.end)
     $scope.searching = false
   });

  }
  
  $scope.download = function(result, i){
  if(!(result.link)){
    if(event) event.preventDefault();
       finded = _.filter($scope.visible,function(item){ return item.id === result.id })
      _.each(finded,function(item){ return item.download =  true })
       finded = _.filter($scope.results,function(item){ return item.id === result.id })
      _.each(finded,function(item){ return item.download =  true })
   name = result.title
   $http.jsonp(url_base+ "/" + url_down + result.id + "&name=" + name).success(function(data){
          if(data.download){
            finded = _.filter($scope.visible,function(item){ return item.id === data.id })
            _.each(finded,function(item){ return item.link =  url_base +'/' + name + ".mp3" })
             finded = _.filter($scope.results,function(item){ return item.id === data.id })
            _.each(finded,function(item){ return item.link =  url_base +'/' + name + ".mp3" })

          }else{
          
          }
      finded = _.filter($scope.visible,function(item){ return item.id === result.id })
      _.each(finded,function(item){ return item.download =  false })
       finded = _.filter($scope.results,function(item){ return item.id === result.id })
      _.each(finded,function(item){ return item.download =  false })
   });

  }
}

  
})