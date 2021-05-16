const map = new AMap.Map('container', {
    mapStyle: 'amap://styles/grey',
    resizeEnable: true,
    center: [116.397732, 39.912152],
    zoom: 14,
});


let allLines = [];

let allPaths = {
    chengdu: [],
    beijing: [],
    tianjin: [],
    hangzhou: [],
    shanghai: [],
    wuhan: [],
    chongqing: [],
    guangzhou: []
};

const allCitys = new Map(
    [
        ['成都', 'chengdu'],
        ['北京', 'beijing'],
        ['天津', 'tianjin'],
        ['杭州', 'hangzhou'],
        ['上海', 'shanghai'],
        ['武汉', 'wuhan'],
        ['重庆', 'chongqing'],
        ['广州', 'guangzhou']
    ]
)

let transOptions = {
    map: map,
    city: '北京市',
    cityd: '北京市',
    panel: 'panel',
    policy: AMap.TransferPolicy.LEAST_TIME //乘车策略
};

//构造公交换乘类
var transfer = new AMap.Transfer(transOptions);


function lineSearch_Callback(data) {
    // const lineArr = data.lineInfo;
    // const lineNum = data.lineInfo.length;
    drawbusLine(data);
    // if (lineNum == 0) {} else {
    //     for (let i = 0; i < lineNum; i++) {
    //         const pathArr = lineArr[i].path;
    //         if (i == 0) //只画单向
    //             drawbusLine(pathArr);
    //     }
    // }
}

function drawbusLine(BusArr) {
    busPolyline = new AMap.Polyline({
        map: map,
        path: BusArr,
        strokeColor: "#09f", //线颜色
        strokeOpacity: 0.8, //线透明度
        // isOutline: true,
        // outlineColor: 'white',
        strokeWeight: 1 //线宽
    });
    map.setFitView();
}

const simpleDrawLines = (city, nameArr) => {
    const linesearch = new AMap.LineSearch({
        pageIndex: 1,
        city,
        pageSize: 2,
        extensions: 'all'
    });

    function lineSearch() {
        nameArr.forEach(name => {
            if (!name) return;
            linesearch.search(name, function (status, result) {
                if (status === 'complete' && result.info === 'OK') {
                    allPaths[city][name] = result.lineInfo[0].path;
                    lineSearch_Callback(result.lineInfo[0].path);
                } else {
                    console.log(result);
                }
            });
        });
    }

    if (allPaths[city].length) {
        lineSearch_Callback(allPaths[city])
    } else {
        lineSearch();
    }
}

const funcStart = (city) => {
    $.get(`http://127.0.0.1:6240/linenames?city=${city}`, function (data) {
        const info = JSON.parse(data);
        allLines = info;
        simpleDrawLines(city, allLines);
    })
}


$('#search').on('click', () => {
    const cityName = $('#cityName').val();
    transOptions.city = cityName;
    if (allCitys.get(cityName)) {
        map.clearMap();
        funcStart(allCitys.get(cityName));
    } else {
        alert('请输入支持的城市名')
    }
})

$('#searchLine').on('click', () => {
    const start = $('#start').val();
    const end = $('#end').val();
    //根据起、终点名称查询公交换乘路线
    transfer.search(
        [{
            keyword: start,
        }, {
            //第一个元素city缺省时取transOptions的city属性
            keyword: end,
        }],
        //第二个元素city缺省时取transOptions的cityd属性
        function (status, result) {
            // result即是对应的公交路线数据信息，相关数据结构文档请参考  https://lbs.amap.com/api/javascript-api/reference/route-search#m_TransferResult
            if (status === 'complete') {
                console.log('绘制公交路线完成')
            } else {
                console.log('公交路线数据查询失败' + result)
            }
        }
    );
})
const start = () => {
    map.clearMap();
}