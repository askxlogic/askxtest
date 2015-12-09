//
//  exampleTests.m
//  exampleTests
//
//  Created by Alexey Kononchuk on 08/12/15.
//  Copyright © 2015 Organization. All rights reserved.
//

#import <XCTest/XCTest.h>

@interface exampleTests : XCTestCase

@end

@implementation exampleTests

- (void)setUp {
    [super setUp];
    // Put setup code here. This method is called before the invocation of each test method in the class.
}

- (void)tearDown {
    // Put teardown code here. This method is called after the invocation of each test method in the class.
    [super tearDown];
}

- (void)testUsual {
    NSLog(@"Usual test");
    XCTAssert(YES,@"Passed");
}

- (void)testStrong {
    NSLog(@"STRONG TEST");
    XCTAssert(YES,@"Passed");
}

@end
